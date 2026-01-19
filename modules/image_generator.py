"""
Image Generator Module
Uses Replicate API (US-based) for FLUX image generation

API: https://replicate.com/black-forest-labs/flux-schnell
Pricing: ~$0.003 per image

Environment variable: REPLICATE_API_TOKEN
"""
import os
import time
from pathlib import Path
from typing import List, Optional

import numpy as np
import requests
from PIL import Image, ImageDraw, ImageFont

import config
from modules.models import Topic

# Image generation constants
IMAGE_SIZE = 1024
MAX_PROMPT_DISPLAY_CHARS = 200
LINE_WRAP_CHARS = 40
LINE_HEIGHT_PX = 30
MAX_DISPLAY_LINES = 6
DOWNLOAD_CHUNK_SIZE = 8192

# Replicate API configuration
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN", "")
REPLICATE_FLUX_MODEL = "black-forest-labs/flux-schnell"


def generate_image_replicate(prompt: str, output_path: Path) -> bool:
    """
    Generate image using Replicate API (FLUX model)

    Args:
        prompt: Image generation prompt
        output_path: Path to save the generated image

    Returns:
        True if successful, False otherwise
    """
    if not REPLICATE_API_TOKEN:
        print("⚠ REPLICATE_API_TOKEN not set, using placeholder")
        return generate_placeholder(prompt, output_path)

    try:
        # Create prediction
        headers = {
            "Authorization": f"Bearer {REPLICATE_API_TOKEN}",
            "Content-Type": "application/json",
        }

        response = requests.post(
            "https://api.replicate.com/v1/models/black-forest-labs/flux-schnell/predictions",
            headers=headers,
            json={
                "input": {
                    "prompt": prompt,
                    "num_outputs": 1,
                    "aspect_ratio": "1:1",
                    "output_format": "png",
                    "output_quality": 90,
                }
            },
            timeout=30
        )
        response.raise_for_status()
        prediction = response.json()

        # Poll for completion
        prediction_url = prediction.get("urls", {}).get("get")
        if not prediction_url:
            print("  ⚠ No prediction URL returned")
            return generate_placeholder(prompt, output_path)

        # Wait for image generation (max 60 seconds)
        for _ in range(30):
            time.sleep(2)
            status_response = requests.get(prediction_url, headers=headers, timeout=10)
            status_response.raise_for_status()
            status = status_response.json()

            if status.get("status") == "succeeded":
                output = status.get("output")
                if output and len(output) > 0:
                    image_url = output[0]
                    # Download image with streaming
                    with requests.get(image_url, timeout=30, stream=True) as img_response:
                        img_response.raise_for_status()
                        with open(output_path, 'wb') as f:
                            for chunk in img_response.iter_content(chunk_size=DOWNLOAD_CHUNK_SIZE):
                                f.write(chunk)
                    return True

            elif status.get("status") == "failed":
                print(f"  ⚠ Generation failed: {status.get('error')}")
                return generate_placeholder(prompt, output_path)

        print("  ⚠ Generation timed out")
        return generate_placeholder(prompt, output_path)

    except Exception as e:
        print(f"  ⚠ Generation error: {e}")
        return generate_placeholder(prompt, output_path)


def generate_placeholder(prompt: str, output_path: Path) -> bool:
    """Generate a placeholder image when API is unavailable"""
    try:
        # Create gradient background using NumPy (O(n) instead of O(n²))
        height, width = IMAGE_SIZE, IMAGE_SIZE

        # Generate gradient values for each row
        y_values = np.linspace(0, 1, height).reshape(-1, 1)

        # Create RGB channels with gradient
        r_channel = (20 + y_values * 30).astype(np.uint8)
        g_channel = (30 + y_values * 40).astype(np.uint8)
        b_channel = (80 + y_values * 60).astype(np.uint8)

        # Broadcast to full width and stack channels
        img_array = np.zeros((height, width, 3), dtype=np.uint8)
        img_array[:, :, 0] = np.broadcast_to(r_channel, (height, width))
        img_array[:, :, 1] = np.broadcast_to(g_channel, (height, width))
        img_array[:, :, 2] = np.broadcast_to(b_channel, (height, width))

        img = Image.fromarray(img_array)
        draw = ImageDraw.Draw(img)

        # Add text
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
        except OSError:
            font = ImageFont.load_default()

        # Wrap prompt text
        words = prompt[:MAX_PROMPT_DISPLAY_CHARS].split()
        lines = []
        current_line = []
        for word in words:
            current_line.append(word)
            if len(" ".join(current_line)) > LINE_WRAP_CHARS:
                lines.append(" ".join(current_line[:-1]))
                current_line = [word]
        if current_line:
            lines.append(" ".join(current_line))

        y_pos = height // 2 - len(lines) * (LINE_HEIGHT_PX // 2)
        for line in lines[:MAX_DISPLAY_LINES]:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x_pos = (width - text_width) // 2
            draw.text((x_pos, y_pos), line, fill=(200, 200, 220), font=font)
            y_pos += LINE_HEIGHT_PX

        # Add "PLACEHOLDER" watermark
        draw.text((width // 2 - 80, height - 60), "[ PLACEHOLDER ]",
                  fill=(100, 100, 120), font=font)

        img.save(output_path, "PNG")
        return True

    except Exception as e:
        print(f"  ⚠ Placeholder creation failed: {e}")
        return False


def batch_generate_images(topics: List[Topic], output_dir: Path) -> List[Topic]:
    """
    Generate images for all topics

    Args:
        topics: List of Topic objects with image_prompt field
        output_dir: Directory to save images

    Returns:
        Topics with image_path and image_filename fields populated
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"🖼️  Generating {len(topics)} images...")

    for i, topic in enumerate(topics, 1):
        prompt = topic.image_prompt or "futuristic AI technology visualization"
        filename = f"topic_{i:02d}.png"
        output_path = output_dir / filename

        print(f"   [{i}/{len(topics)}] {topic.title[:30]}...", end=" ")

        success = generate_image_replicate(prompt, output_path)

        if success:
            print("✓")
            topic.image_path = str(output_path)
            topic.image_filename = filename
        else:
            print("✗")
            topic.image_path = None
            topic.image_filename = None

        # Rate limiting
        if i < len(topics):
            time.sleep(1)

    successful = sum(1 for t in topics if t.image_path)
    print(f"\n✅ Generated {successful}/{len(topics)} images")

    return topics


if __name__ == "__main__":
    # Test
    test_topics = [
        Topic(
            title="测试话题",
            title_en="Test Topic",
            description="A test topic",
            image_prompt="Futuristic AI brain visualization, neural networks, blue glow"
        )
    ]

    output_dir = Path("./test_images")
    result = batch_generate_images(test_topics, output_dir)
    print(f"Result: {[t.to_dict() for t in result]}")
