<p align="center">
  <img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="MIT License">
  <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" alt="PRs Welcome">
</p>

<h1 align="center">🌐 Meridian</h1>

<p align="center">
  <strong>AI-powered newsletter generator that transforms scattered signals into clarity</strong>
</p>

<p align="center">
  Collect from multiple sources • Summarize with Claude • Generate visuals • Export anywhere
</p>

---

## What is Meridian?

Meridian is an intelligent newsletter pipeline that automatically collects AI news from various sources, synthesizes insights using Claude, and generates beautiful multilingual reports with AI-generated visuals.

Like a meridian line that provides a reference point for navigation, this tool helps you find your bearings in the fast-moving AI landscape.

## ✨ Features

- **🔌 Pluggable Sources** — Reddit (built-in), with architecture ready for Twitter, HN, RSS, and more
- **🤖 Claude-Powered Analysis** — Professional summaries and trend extraction in any language
- **🎨 AI Visuals** — FLUX-generated images via Replicate for each topic
- **📝 Multi-Format Export** — Obsidian markdown, HTML, and extensible to email/PDF
- **🌍 Multilingual Ready** — English default, easily configurable for any language
- **⚡ Fast & Efficient** — Connection pooling, streaming downloads, optimized API usage

## 🚀 Quick Start

```bash
# Clone
git clone https://github.com/raullenchai/meridian.git
cd meridian

# Setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configure
export ANTHROPIC_API_KEY="your-claude-api-key"

# Run
python main.py
```

## 📖 Usage

```bash
# Full pipeline with images
python main.py

# Quick run without images
python main.py --skip-images

# Use Reddit API (faster, requires credentials)
python main.py --reddit-api

# Test mode with sample data
python main.py --skip-reddit --skip-images
```

## ⚙️ Configuration

### Environment Variables

| Variable | Required | Description |
|----------|:--------:|-------------|
| `ANTHROPIC_API_KEY` | ✅ | Claude API key ([get one](https://console.anthropic.com)) |
| `REPLICATE_API_TOKEN` | — | For AI image generation ([get one](https://replicate.com/account/api-tokens)) |
| `REDDIT_CLIENT_ID` | — | Reddit API client ID |
| `REDDIT_CLIENT_SECRET` | — | Reddit API secret |

### Customization

Edit `config.py` to customize:

```python
# Sources to monitor
REDDIT_SUBREDDITS = ["MachineLearning", "LocalLLaMA", ...]

# Number of topics to extract
TOP_TOPICS_COUNT = 10

# Claude model
CLAUDE_MODEL = "claude-sonnet-4-20250514"
```

## 📁 Output

```
output/
├── index.html      # Beautiful dark-themed web preview
├── ai-news.md      # Obsidian-ready markdown with embeds
└── images/         # AI-generated topic illustrations
    ├── topic_01.png
    ├── topic_02.png
    └── ...
```

📂 **[See example output →](examples/)**

## 🏗️ Architecture

```
meridian/
├── main.py                 # Pipeline orchestrator
├── config.py               # Configuration
├── modules/
│   ├── reddit_collector.py # Reddit scraping & API
│   ├── claude_summarizer.py# Summarization & topic extraction
│   ├── prompt_generator.py # Image prompt generation
│   ├── image_generator.py  # Replicate FLUX integration
│   ├── obsidian_saver.py   # Markdown export
│   ├── html_generator.py   # HTML generation
│   └── models.py           # Data models
└── output/                 # Generated content
```

### Pipeline Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Sources   │────▶│   Claude    │────▶│   Export    │
│  (Reddit)   │     │  Analysis   │     │ (MD/HTML)   │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │   Images    │
                    │  (FLUX)     │
                    └─────────────┘
```

## 🔌 Adding New Sources

Meridian is designed to be extensible. To add a new source:

1. Create `modules/your_source_collector.py`
2. Implement `collect_posts() -> List[Post]`
3. Register in `main.py`

```python
# Example: modules/hackernews_collector.py
def collect_posts(limit: int = 50) -> List[Post]:
    # Your implementation
    pass
```

## 🛣️ Roadmap

- [ ] Hacker News source
- [ ] Twitter/X source
- [ ] RSS feed source
- [ ] Email newsletter export
- [ ] PDF export
- [ ] Scheduled runs (cron)
- [ ] Web dashboard
- [ ] Multi-language output selection

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) first.

```bash
# Fork, clone, then:
git checkout -b feature/amazing-feature
# Make your changes
git commit -m "Add amazing feature"
git push origin feature/amazing-feature
# Open a PR
```

## 📄 License

MIT © 2025 — See [LICENSE](LICENSE) for details.

---

<p align="center">
  <sub>Built with ☕ and Claude</sub>
</p>
