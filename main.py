#!/usr/bin/env python3
"""
Meridian - AI Newsletter Generator
==================================
Collects AI news from multiple sources, synthesizes insights with Claude,
generates visuals, and exports to Obsidian markdown + HTML.

Usage:
    python main.py [--skip-images] [--skip-reddit] [--reddit-api]

Environment Variables:
    ANTHROPIC_API_KEY      - Claude API key (required)
    REPLICATE_API_TOKEN    - Replicate API for images (optional)
    REDDIT_CLIENT_ID       - Reddit API credentials (optional)
    REDDIT_CLIENT_SECRET   - Reddit API credentials (optional)
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

import config
from modules.models import Topic
from modules.reddit_collector import collect_all_posts, posts_to_text
from modules.claude_summarizer import summarize_posts, extract_top_topics
from modules.prompt_generator import generate_image_prompts
from modules.image_generator import batch_generate_images
from modules.obsidian_saver import create_markdown_note
from modules.html_generator import generate_html_page


def print_banner():
    """Print startup banner"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                     🌐 M E R I D I A N                       ║
║                                                              ║
║        AI-powered newsletter generator                       ║
║        Transforming scattered signals into clarity           ║
╚══════════════════════════════════════════════════════════════╝
""")


def check_api_keys() -> bool:
    """Check if required API keys are set"""
    if not config.ANTHROPIC_API_KEY:
        print("❌ Error: ANTHROPIC_API_KEY environment variable not set")
        print("   Set it with: export ANTHROPIC_API_KEY='your-key'")
        return False

    if not config.REPLICATE_API_TOKEN:
        print("⚠️  Warning: REPLICATE_API_TOKEN not set - will use placeholder images")
        print("   Get token at: https://replicate.com/account/api-tokens")

    return True


def print_step_header(step_num: int, title: str):
    """Print a formatted step header"""
    print(f"\n{'='*60}")
    print(f"STEP {step_num}: {title}")
    print("="*60)


def collect_posts_step(skip_reddit: bool, use_reddit_api: bool = False) -> Tuple[str, int]:
    """Step 1: Collect Reddit posts"""
    print_step_header(1, "Collecting AI Hot Topics from Reddit")

    if skip_reddit:
        print("⏭️  Skipping Reddit (using sample data)")
        posts_text = get_sample_posts()
        post_count = 20
    else:
        posts = collect_all_posts(use_api=use_reddit_api)
        posts_text = posts_to_text(posts)
        post_count = len(posts)

    print(f"\n📊 Collected {post_count} posts")
    return posts_text, post_count


def summarize_step(posts_text: str) -> str:
    """Step 2: Generate Chinese summary"""
    print_step_header(2, "Generating Chinese Summary with Claude")
    summary = summarize_posts(posts_text)
    print(f"\n📝 Summary length: {len(summary)} characters")
    return summary


def extract_topics_step(posts_text: str) -> List[Topic]:
    """Step 3: Extract Top 10 topics"""
    print_step_header(3, "Extracting Top 10 Important Topics")
    topics = extract_top_topics(posts_text, config.TOP_TOPICS_COUNT)

    print(f"\n🔥 Extracted {len(topics)} topics:")
    for i, t in enumerate(topics, 1):
        print(f"   {i}. {t.title}")

    return topics


def generate_prompts_step(topics: List[Topic]) -> List[Topic]:
    """Step 4: Generate image prompts"""
    print_step_header(4, "Generating Professional Image Prompts")
    return generate_image_prompts(topics)


def generate_images_step(topics: List[Topic], skip_images: bool) -> List[Topic]:
    """Step 5: Generate images with ModelScope"""
    print_step_header(5, "Generating Images with ModelScope FLUX")

    if skip_images:
        print("⏭️  Skipping image generation")
        for topic in topics:
            topic.image_filename = None
            topic.image_path = None
        return topics

    return batch_generate_images(topics, config.IMAGES_DIR)


def save_markdown_step(topics: List[Topic], summary: str) -> str:
    """Step 6: Save to Obsidian format"""
    print_step_header(6, "Creating Obsidian Markdown Note")
    return create_markdown_note(
        topics=topics,
        summary=summary,
        output_path=config.MARKDOWN_OUTPUT,
        images_dir=config.IMAGES_DIR
    )


def generate_html_step(topics: List[Topic], summary: str) -> str:
    """Step 7: Generate HTML preview"""
    print_step_header(7, "Creating HTML Display Page")
    return generate_html_page(
        topics=topics,
        summary=summary,
        output_path=config.HTML_OUTPUT,
        images_dir=config.IMAGES_DIR
    )


def print_completion_summary(
    post_count: int,
    topics: List[Topic],
    md_path: str,
    html_path: str,
    elapsed_seconds: int
):
    """Print final completion summary"""
    print("\n" + "="*60)
    print("✅ PIPELINE COMPLETE!")
    print("="*60)

    images_generated = sum(1 for t in topics if t.image_path)

    print(f"""
📊 Summary:
   • Posts collected: {post_count}
   • Topics extracted: {len(topics)}
   • Images generated: {images_generated}
   • Time elapsed: {elapsed_seconds}s

📁 Output files:
   • Markdown: {md_path}
   • HTML: {html_path}
   • Images: {config.IMAGES_DIR}

🎨 Open in browser:
   file://{html_path}

📝 Copy to Obsidian:
   cp -r {config.OUTPUT_DIR}/* ~/your-obsidian-vault/
""")


def run_pipeline(
    skip_images: bool = False,
    skip_reddit: bool = False,
    use_reddit_api: bool = False
) -> bool:
    """
    Run the complete AI news pipeline

    Args:
        skip_images: Skip image generation step
        skip_reddit: Use sample data instead of scraping Reddit
        use_reddit_api: Use Reddit API instead of web scraping

    Returns:
        True if successful, False otherwise
    """
    print_banner()

    if not check_api_keys():
        return False

    start_time = datetime.now()

    # Ensure output directories exist
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    config.IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    try:
        # Execute pipeline steps
        posts_text, post_count = collect_posts_step(skip_reddit, use_reddit_api)
        summary = summarize_step(posts_text)
        topics = extract_topics_step(posts_text)
        topics = generate_prompts_step(topics)
        topics = generate_images_step(topics, skip_images)
        md_path = save_markdown_step(topics, summary)
        html_path = generate_html_step(topics, summary)

        # Print completion summary
        elapsed = datetime.now() - start_time
        print_completion_summary(post_count, topics, md_path, html_path, elapsed.seconds)

        return True

    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline interrupted by user")
        return False

    except Exception as e:
        print(f"\n\n❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def get_sample_posts() -> str:
    """Return sample posts for testing"""
    return """
1. [MachineLearning] Claude 3.5 Sonnet achieves state-of-the-art on multiple benchmarks (Score: 2341, Comments: 456)
2. [LocalLLaMA] Llama 3.1 405B running locally - my experience and benchmarks (Score: 1876, Comments: 324)
3. [OpenAI] GPT-5 reportedly in final testing phase, expected Q1 2025 (Score: 1654, Comments: 543)
4. [artificial] Google DeepMind's new paper on AI safety gets mixed reactions (Score: 1432, Comments: 287)
5. [ChatGPT] Custom GPTs now support real-time data access (Score: 1298, Comments: 198)
6. [StableDiffusion] FLUX.1 Pro comparison with SDXL - detailed analysis (Score: 1187, Comments: 234)
7. [singularity] AI researchers predict AGI timeline moved up by 2 years (Score: 1098, Comments: 456)
8. [ClaudeAI] Claude's new computer use feature is mind-blowing (Score: 987, Comments: 178)
9. [MachineLearning] New paper: Attention is NOT all you need - alternative architectures (Score: 876, Comments: 234)
10. [deeplearning] NVIDIA announces next-gen AI chips with 2x performance (Score: 823, Comments: 156)
11. [LocalLLaMA] Best practices for fine-tuning Llama on consumer GPUs (Score: 765, Comments: 143)
12. [OpenAI] OpenAI's new reasoning model shows emergent capabilities (Score: 732, Comments: 198)
13. [artificial] EU AI Act enforcement begins - what you need to know (Score: 698, Comments: 234)
14. [ChatGPT] Voice mode now available to all users globally (Score: 654, Comments: 123)
15. [ArtificialIntelligence] Microsoft and OpenAI $100B data center plan confirmed (Score: 621, Comments: 187)
16. [MachineLearning] Mixture of Experts scaling laws - new research insights (Score: 598, Comments: 145)
17. [StableDiffusion] ComfyUI workflow for consistent characters across images (Score: 567, Comments: 98)
18. [singularity] AI coding assistants now write 30% of new code at major companies (Score: 543, Comments: 234)
19. [LocalLLaMA] MLX optimizations for Apple Silicon - 2x speed improvement (Score: 512, Comments: 87)
20. [deeplearning] State Space Models vs Transformers - comprehensive comparison (Score: 487, Comments: 156)
"""


def main():
    parser = argparse.ArgumentParser(
        description="Meridian - AI Newsletter Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Full pipeline (scraping + images)
  python main.py --skip-images      # Skip image generation
  python main.py --skip-reddit      # Use sample data (for testing)
  python main.py --reddit-api       # Use Reddit API instead of scraping

Environment Variables:
  ANTHROPIC_API_KEY     Claude API key (required)
  REPLICATE_API_TOKEN   Replicate API for images (optional)
  REDDIT_CLIENT_ID      Reddit API client ID (optional)
  REDDIT_CLIENT_SECRET  Reddit API client secret (optional)
        """
    )

    parser.add_argument(
        "--skip-images",
        action="store_true",
        help="Skip image generation step"
    )

    parser.add_argument(
        "--skip-reddit",
        action="store_true",
        help="Use sample data instead of scraping Reddit"
    )

    parser.add_argument(
        "--reddit-api",
        action="store_true",
        help="Use Reddit API instead of web scraping (requires REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET)"
    )

    args = parser.parse_args()

    success = run_pipeline(
        skip_images=args.skip_images,
        skip_reddit=args.skip_reddit,
        use_reddit_api=args.reddit_api
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
