"""
HTML Display Page Generator
Creates a responsive grid preview page
"""
from datetime import datetime
from html import escape
from pathlib import Path
from typing import List

import config
from modules.models import Topic

# Constants
DESCRIPTION_PREVIEW_LENGTH = 150


def safe_html(text: str) -> str:
    """Escape text for safe HTML insertion, preventing XSS"""
    return escape(str(text), quote=True)


def generate_html_page(
    topics: List[Topic],
    summary: str,
    output_path: Path,
    images_dir: Path
) -> str:
    """
    Generate a responsive HTML page with grid preview

    Args:
        topics: List of Topic objects
        summary: Chinese summary text
        output_path: Path to save HTML file
        images_dir: Directory containing images

    Returns:
        Path to generated HTML file
    """
    print("🌐 Generating HTML display page...")

    today = datetime.now()
    date_display = today.strftime("%B %d, %Y")

    # Generate topic cards
    cards_html = []
    for i, topic in enumerate(topics, 1):
        title = safe_html(topic.title)
        description = safe_html(topic.description)
        keywords = [safe_html(k) for k in topic.keywords]
        importance = min(topic.importance, 10)
        image_filename = topic.image_filename or ""

        image_src = f"images/{safe_html(image_filename)}" if image_filename else ""
        stars = "⭐" * importance
        keywords_html = " ".join([f'<span class="keyword">{k}</span>' for k in keywords[:5]])

        card = f'''
        <div class="card">
            <div class="card-image">
                {"<img src='" + image_src + "' alt='" + title + "' loading='lazy'>" if image_src else "<div class='placeholder'>Image generating...</div>"}
            </div>
            <div class="card-content">
                <h3>{i}. {title}</h3>
                <div class="importance">{stars}</div>
                <p>{description[:DESCRIPTION_PREVIEW_LENGTH]}{"..." if len(description) > DESCRIPTION_PREVIEW_LENGTH else ""}</p>
                <div class="keywords">{keywords_html}</div>
            </div>
        </div>'''
        cards_html.append(card)

    # Format summary with paragraphs (escape for XSS protection)
    summary_escaped = safe_html(summary)
    summary_html = "</p><p>".join(summary_escaped.split("\n\n"))
    summary_html = f"<p>{summary_html}</p>"

    html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI News Digest - {date_display}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            color: #e0e0e0;
            padding: 20px;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        header {{
            text-align: center;
            padding: 40px 20px;
            margin-bottom: 30px;
        }}

        h1 {{
            font-size: 2.5rem;
            background: linear-gradient(90deg, #00d4ff, #7b2ff7);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 10px;
        }}

        .subtitle {{
            color: #888;
            font-size: 1rem;
        }}

        .summary-section {{
            background: rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 40px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}

        .summary-section h2 {{
            color: #00d4ff;
            margin-bottom: 20px;
            font-size: 1.5rem;
        }}

        .summary-section p {{
            line-height: 1.8;
            margin-bottom: 15px;
            color: #ccc;
        }}

        .grid-section h2 {{
            color: #00d4ff;
            margin-bottom: 25px;
            font-size: 1.5rem;
            text-align: center;
        }}

        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 25px;
            padding: 10px;
        }}

        .card {{
            background: rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}

        .card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
            border-color: rgba(0, 212, 255, 0.3);
        }}

        .card-image {{
            width: 100%;
            height: 200px;
            overflow: hidden;
            background: rgba(0, 0, 0, 0.2);
        }}

        .card-image img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.3s ease;
        }}

        .card:hover .card-image img {{
            transform: scale(1.05);
        }}

        .card-image .placeholder {{
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #666;
            font-size: 0.9rem;
        }}

        .card-content {{
            padding: 20px;
        }}

        .card-content h3 {{
            color: #fff;
            font-size: 1.1rem;
            margin-bottom: 10px;
            line-height: 1.4;
        }}

        .importance {{
            margin-bottom: 10px;
            font-size: 0.9rem;
        }}

        .card-content p {{
            color: #aaa;
            font-size: 0.9rem;
            line-height: 1.6;
            margin-bottom: 15px;
        }}

        .keywords {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }}

        .keyword {{
            background: rgba(0, 212, 255, 0.15);
            color: #00d4ff;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.75rem;
        }}

        footer {{
            text-align: center;
            padding: 40px 20px;
            color: #666;
            font-size: 0.85rem;
        }}

        footer a {{
            color: #00d4ff;
            text-decoration: none;
        }}

        @media (max-width: 768px) {{
            h1 {{
                font-size: 1.8rem;
            }}

            .grid {{
                grid-template-columns: 1fr;
            }}

            .summary-section {{
                padding: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🤖 AI News Digest</h1>
            <p class="subtitle">{date_display} · Auto-generated from Reddit AI Communities</p>
        </header>

        <section class="summary-section">
            <h2>📊 Trend Summary</h2>
            {summary_html}
        </section>

        <section class="grid-section">
            <h2>🔥 Top {len(topics)} Topics</h2>
            <div class="grid">
                {"".join(cards_html)}
            </div>
        </section>

        <footer>
            <p>Auto-generated by Meridian · Powered by Claude API + Replicate</p>
            <p style="margin-top: 10px;">Source: Reddit ·
                r/MachineLearning · r/LocalLLaMA · r/ChatGPT · r/OpenAI
            </p>
        </footer>
    </div>
</body>
</html>'''

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html_content, encoding="utf-8")

    print(f"✅ HTML page saved: {output_path}")

    return str(output_path)


if __name__ == "__main__":
    # Test
    test_topics = [
        Topic(
            title="GPT-5 即将发布",
            title_en="GPT-5 Release",
            description="OpenAI 预计将在近期发布新一代语言模型，性能提升显著。",
            keywords=["GPT-5", "OpenAI", "LLM"],
            importance=9,
            image_filename="topic_01.png"
        ),
        Topic(
            title="开源 AI 模型崛起",
            title_en="Rise of Open Source AI",
            description="Llama 3 和其他开源模型正在改变 AI 格局。",
            keywords=["Llama", "开源", "Meta"],
            importance=8,
            image_filename="topic_02.png"
        )
    ]

    test_summary = "本周AI领域最热门的话题包括GPT-5的发布传闻和开源模型的快速发展..."

    output = Path("./test_output/index.html")
    generate_html_page(test_topics, test_summary, output, Path("./test_output/images"))
