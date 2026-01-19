"""
Image Prompt Generator
Generates professional prompts for AI image generation
"""
import json
from typing import List

import anthropic

import config
from modules.models import Topic
from modules.claude_summarizer import create_client


def generate_image_prompts(topics: List[Topic]) -> List[Topic]:
    """
    Generate professional image prompts for each topic

    Args:
        topics: List of Topic objects

    Returns:
        List of topics with image_prompt field populated
    """
    client = create_client()

    print("🎨 Generating image prompts...")

    # Create batch prompt for efficiency
    topics_info = "\n".join([
        f"{i+1}. {t.title_en or t.title} - Keywords: {', '.join(t.keywords or ['AI'])}"
        for i, t in enumerate(topics)
    ])

    prompt = f"""Generate professional image prompts for the following {len(topics)} AI topics, for use with the FLUX image generation model.

Topics:
{topics_info}

Requirements:
1. Each prompt should be in English
2. Style: modern tech aesthetic, futuristic, professional
3. Include specific visual element descriptions
4. Length: 50-100 words
5. Avoid text/letters appearing in the image

Return in JSON format, containing only the prompt array:
[
  "prompt for topic 1...",
  "prompt for topic 2...",
  ...
]

Return only the JSON array, no other content."""

    message = client.messages.create(
        model=config.CLAUDE_MODEL,
        max_tokens=3000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    response_text = message.content[0].text

    # Parse JSON
    try:
        start = response_text.find("[")
        end = response_text.rfind("]") + 1
        if start >= 0 and end > start:
            prompts = json.loads(response_text[start:end])
        else:
            prompts = json.loads(response_text)
    except json.JSONDecodeError:
        # Fallback: generate simple prompts
        prompts = [
            f"Futuristic technology visualization of {t.title_en or 'AI'}, "
            f"digital art, blue and purple color scheme, glowing elements, "
            f"abstract data visualization, professional tech illustration, 8k, detailed"
            for t in topics
        ]

    # Add prompts to topics
    for i, topic in enumerate(topics):
        if i < len(prompts):
            topic.image_prompt = prompts[i]
        else:
            topic.image_prompt = get_fallback_prompt(topic)

    print(f"✅ Generated {len(topics)} image prompts")

    return topics


def get_fallback_prompt(topic: Topic) -> str:
    """Generate a fallback prompt for a topic"""
    keywords = topic.keywords or ["AI", "technology"]
    title = topic.title_en or "AI Technology"

    return (
        f"Abstract digital visualization representing {title}, "
        f"featuring {', '.join(keywords[:3])}, "
        f"futuristic tech aesthetic, glowing neural network patterns, "
        f"deep blue and cyan color palette, volumetric lighting, "
        f"professional concept art, 8k ultra detailed, trending on artstation"
    )


if __name__ == "__main__":
    # Test
    test_topics = [
        Topic(
            title="GPT-5发布",
            title_en="GPT-5 Release",
            description="OpenAI即将发布新一代语言模型",
            keywords=["GPT-5", "OpenAI", "LLM"]
        ),
        Topic(
            title="开源AI崛起",
            title_en="Rise of Open Source AI",
            description="开源AI模型正在改变格局",
            keywords=["open source", "Llama", "community"]
        )
    ]

    result = generate_image_prompts(test_topics)
    for t in result:
        print(f"\n{t.title}:")
        print(f"  Prompt: {t.image_prompt[:100] if t.image_prompt else 'None'}...")
