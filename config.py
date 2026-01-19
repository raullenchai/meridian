"""
Meridian - AI Newsletter Generator
Configuration Settings
"""
import os
from pathlib import Path

# Reddit Configuration
# Web scraping (default)
REDDIT_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"

# Reddit API (optional) - Get credentials at: https://www.reddit.com/prefs/apps
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
REDDIT_API_USER_AGENT = "Meridian/1.0"

REDDIT_SUBREDDITS = [
    "MachineLearning",
    "artificial",
    "LocalLLaMA",
    "ChatGPT",
    "OpenAI",
    "ClaudeAI",
    "StableDiffusion",
    "singularity",
    "Futurology",
    "deeplearning"
]
REDDIT_POST_LIMIT = 15  # Per subreddit (~150 total)

# Claude API Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = "claude-sonnet-4-20250514"

# Replicate API Configuration (US-based, has FLUX)
# Get token at: https://replicate.com/account/api-tokens
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN", "")

# Output Configuration
OUTPUT_DIR = Path(__file__).parent / "output"
IMAGES_DIR = OUTPUT_DIR / "images"
HTML_OUTPUT = OUTPUT_DIR / "index.html"
MARKDOWN_OUTPUT = OUTPUT_DIR / "ai-news.md"

# Number of top topics to extract
TOP_TOPICS_COUNT = 10
