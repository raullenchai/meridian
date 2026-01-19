"""
Claude API Chinese Summarizer
Uses Claude to summarize Reddit AI news in Chinese
"""
import json
from typing import List

import anthropic

import config
from modules.models import Topic

# Constants
MAX_TOPIC_COUNT = 50
MIN_TOPIC_COUNT = 1


def create_client() -> anthropic.Anthropic:
    """Create Anthropic client"""
    if not config.ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")
    return anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)


def summarize_posts(posts_text: str) -> str:
    """
    Summarize Reddit posts in Chinese

    Args:
        posts_text: Text containing all Reddit post titles and metadata

    Returns:
        Chinese summary of AI trends
    """
    client = create_client()

    print("🤖 Using Claude to generate Chinese summary...")

    prompt = f"""You are a professional AI industry analyst. Analyze the following AI-related posts from Reddit and write a professional trend summary.

Reddit posts:
{posts_text}

Please provide:
1. Overall trend overview (2-3 paragraphs)
2. Key discussion topics
3. Technology development directions
4. Community focus areas

Write in a professional but accessible style, avoiding excessive jargon."""

    message = client.messages.create(
        model=config.CLAUDE_MODEL,
        max_tokens=2000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    summary = message.content[0].text
    print("✅ Summary generated")

    return summary


def extract_top_topics(posts_text: str, count: int = 10) -> List[Topic]:
    """
    Extract top N important topics from posts

    Args:
        posts_text: Text containing all Reddit post titles
        count: Number of topics to extract (must be positive, max 50)

    Returns:
        List of Topic objects
    """
    # Validate count parameter
    count = max(MIN_TOPIC_COUNT, min(count, MAX_TOPIC_COUNT))

    client = create_client()

    print(f"🔍 Extracting Top {count} topics...")

    prompt = f"""Analyze the following Reddit AI posts and extract the {count} most important topics.

Posts:
{posts_text}

Return in JSON format, each topic containing:
- title: Topic title (concise and impactful)
- title_en: English title (for image generation)
- description: Detailed description (2-3 sentences)
- keywords: List of keywords (for image generation)
- importance: Importance score (1-10)

Return only the JSON array, no other content. Example format:
[
  {{
    "title": "GPT-5 Release Imminent",
    "title_en": "GPT-5 Release Imminent",
    "description": "OpenAI is about to release its next-generation language model...",
    "keywords": ["GPT-5", "OpenAI", "language model", "AI"],
    "importance": 9
  }}
]"""

    message = client.messages.create(
        model=config.CLAUDE_MODEL,
        max_tokens=3000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    response_text = message.content[0].text

    # Parse JSON from response
    try:
        # Find JSON array in response
        start = response_text.find("[")
        end = response_text.rfind("]") + 1
        if start >= 0 and end > start:
            topics_data = json.loads(response_text[start:end])
        else:
            topics_data = json.loads(response_text)
    except json.JSONDecodeError as e:
        print(f"  ⚠ JSON parsing error: {e}")
        topics_data = []

    # Convert to Topic objects
    topics = [Topic.from_dict(t) for t in topics_data]

    # Sort by importance
    topics.sort(key=lambda x: x.importance, reverse=True)
    topics = topics[:count]

    print(f"✅ Extracted {len(topics)} topics")

    return topics


if __name__ == "__main__":
    # Test with sample data
    sample = """
    1. [MachineLearning] Claude 3.5 Sonnet beats GPT-4 on benchmarks (Score: 1234)
    2. [LocalLLaMA] Llama 3.1 405B is incredible for local use (Score: 987)
    3. [OpenAI] GPT-5 rumors: Expected capabilities (Score: 876)
    """

    summary = summarize_posts(sample)
    print("\nSummary:")
    print(summary)
