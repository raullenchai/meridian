"""
Reddit AI News Collector
Supports both web scraping (default) and official Reddit API

Web scraping: No setup required, uses old.reddit.com
Reddit API: Requires REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET env vars
           Get credentials at: https://www.reddit.com/prefs/apps
"""
import re
import time
from dataclasses import dataclass
from typing import List, Optional

import requests
from bs4 import BeautifulSoup

import config


@dataclass
class RedditPost:
    """Represents a single Reddit post with metadata."""
    title: str
    score: int
    num_comments: int
    url: str
    subreddit: str
    permalink: str


# ============================================================================
# Session Management
# ============================================================================

_scrape_session: Optional[requests.Session] = None
_api_session: Optional[requests.Session] = None
_api_token: Optional[str] = None
_api_token_expires: float = 0


def get_scrape_session() -> requests.Session:
    """Get or create a requests session for web scraping."""
    global _scrape_session
    if _scrape_session is None:
        _scrape_session = requests.Session()
        _scrape_session.headers.update({
            "User-Agent": config.REDDIT_USER_AGENT,
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "en-US,en;q=0.9",
        })
    return _scrape_session


def get_api_session() -> requests.Session:
    """Get or create a requests session for Reddit API."""
    global _api_session
    if _api_session is None:
        _api_session = requests.Session()
        _api_session.headers.update({
            "User-Agent": config.REDDIT_API_USER_AGENT,
        })
    return _api_session


# ============================================================================
# Reddit API Methods
# ============================================================================

def is_api_available() -> bool:
    """Check if Reddit API credentials are configured."""
    return bool(config.REDDIT_CLIENT_ID and config.REDDIT_CLIENT_SECRET)


def get_api_token() -> Optional[str]:
    """Get OAuth token for Reddit API (cached for 1 hour)."""
    global _api_token, _api_token_expires

    # Return cached token if still valid
    if _api_token and time.time() < _api_token_expires:
        return _api_token

    if not is_api_available():
        return None

    try:
        auth = requests.auth.HTTPBasicAuth(
            config.REDDIT_CLIENT_ID,
            config.REDDIT_CLIENT_SECRET
        )
        data = {
            "grant_type": "client_credentials",
        }
        headers = {
            "User-Agent": config.REDDIT_API_USER_AGENT,
        }

        response = requests.post(
            "https://www.reddit.com/api/v1/access_token",
            auth=auth,
            data=data,
            headers=headers,
            timeout=10
        )
        response.raise_for_status()

        token_data = response.json()
        _api_token = token_data.get("access_token")
        # Token valid for 1 hour, refresh 5 min early
        _api_token_expires = time.time() + token_data.get("expires_in", 3600) - 300

        return _api_token

    except Exception as e:
        print(f"  ⚠ Failed to get Reddit API token: {e}")
        return None


def fetch_subreddit_api(subreddit: str, limit: int = 15) -> List[RedditPost]:
    """Fetch posts from a subreddit using Reddit API."""
    token = get_api_token()
    if not token:
        return []

    session = get_api_session()
    session.headers["Authorization"] = f"Bearer {token}"

    posts = []
    try:
        response = session.get(
            f"https://oauth.reddit.com/r/{subreddit}/hot",
            params={"limit": limit},
            timeout=10
        )
        response.raise_for_status()

        data = response.json()
        for child in data.get("data", {}).get("children", []):
            post_data = child.get("data", {})

            # Skip promoted posts
            if post_data.get("promoted"):
                continue

            posts.append(RedditPost(
                title=post_data.get("title", ""),
                score=post_data.get("score", 0),
                num_comments=post_data.get("num_comments", 0),
                url=post_data.get("url", ""),
                subreddit=subreddit,
                permalink=f"https://reddit.com{post_data.get('permalink', '')}"
            ))

    except Exception as e:
        print(f"  ⚠ API error for r/{subreddit}: {e}")

    return posts


# ============================================================================
# Web Scraping Methods (Default)
# ============================================================================

def scrape_subreddit(subreddit: str, limit: int = 15) -> List[RedditPost]:
    """Scrape posts from a subreddit using old.reddit.com"""
    url = f"https://old.reddit.com/r/{subreddit}/hot/"
    session = get_scrape_session()

    posts = []
    try:
        response = session.get(url, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        things = soup.find_all("div", class_="thing", limit=limit + 5)

        for thing in things[:limit]:
            if "promoted" in thing.get("class", []):
                continue

            title_elem = thing.find("a", class_="title")
            if not title_elem:
                continue

            title = title_elem.get_text(strip=True)
            permalink = thing.get("data-permalink", "")

            # Get score
            score_elem = thing.find("div", class_="score")
            score_text = score_elem.get("title", "0") if score_elem else "0"
            try:
                score = int(score_text) if score_text else 0
            except ValueError:
                score = 0

            # Get comments count
            comments_elem = thing.find("a", class_="comments")
            if comments_elem:
                comments_text = comments_elem.get_text()
                match = re.search(r"(\d+)", comments_text)
                num_comments = int(match.group(1)) if match else 0
            else:
                num_comments = 0

            # Get URL
            post_url = title_elem.get("href", "")
            if post_url.startswith("/"):
                post_url = f"https://reddit.com{post_url}"

            posts.append(RedditPost(
                title=title,
                score=score,
                num_comments=num_comments,
                url=post_url,
                subreddit=subreddit,
                permalink=f"https://reddit.com{permalink}" if permalink else post_url
            ))

    except Exception as e:
        print(f"  ⚠ Error scraping r/{subreddit}: {e}")

    return posts


# ============================================================================
# Main Collection Function
# ============================================================================

def collect_all_posts(use_api: bool = False) -> List[RedditPost]:
    """
    Collect posts from all configured subreddits.

    Args:
        use_api: If True, use Reddit API. If False (default), use web scraping.
                 Falls back to scraping if API is not configured.

    Returns:
        List of RedditPost objects sorted by score
    """
    all_posts = []

    # Determine method
    if use_api:
        if is_api_available():
            method = "api"
            print("📡 Collecting AI hot topics from Reddit (API mode)...")
        else:
            method = "scrape"
            print("📡 Collecting AI hot topics from Reddit (API not configured, using scraping)...")
    else:
        method = "scrape"
        print("📡 Collecting AI hot topics from Reddit (scraping mode)...")

    print(f"   Subreddits: {len(config.REDDIT_SUBREDDITS)}")

    for i, subreddit in enumerate(config.REDDIT_SUBREDDITS, 1):
        print(f"   [{i}/{len(config.REDDIT_SUBREDDITS)}] r/{subreddit}...", end=" ")

        if method == "api":
            posts = fetch_subreddit_api(subreddit, config.REDDIT_POST_LIMIT)
        else:
            posts = scrape_subreddit(subreddit, config.REDDIT_POST_LIMIT)

        all_posts.extend(posts)
        print(f"✓ {len(posts)} posts")

        # Rate limiting
        if i < len(config.REDDIT_SUBREDDITS):
            # API has higher rate limit, can be faster
            delay = 0.6 if method == "api" else 1.5
            time.sleep(delay)

    # Sort by score
    all_posts.sort(key=lambda x: x.score, reverse=True)

    print(f"\n✅ Total collected: {len(all_posts)} posts")
    return all_posts


def posts_to_text(posts: List[RedditPost]) -> str:
    """Convert posts to text for Claude analysis"""
    lines = []
    for i, post in enumerate(posts, 1):
        lines.append(
            f"{i}. [{post.subreddit}] {post.title} "
            f"(Score: {post.score}, Comments: {post.num_comments})"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test Reddit collector")
    parser.add_argument("--api", action="store_true", help="Use Reddit API instead of scraping")
    args = parser.parse_args()

    print(f"API available: {is_api_available()}")
    print(f"Using: {'API' if args.api and is_api_available() else 'Scraping'}\n")

    posts = collect_all_posts(use_api=args.api)
    print("\nTop 10 posts:")
    for post in posts[:10]:
        print(f"  [{post.score:>5}] {post.title[:60]}...")
