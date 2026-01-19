# Contributing to Meridian

Thank you for your interest in contributing to Meridian! This document provides guidelines and information for contributors.

## Code of Conduct

Be respectful, inclusive, and constructive. We're all here to build something useful together.

## How to Contribute

### Reporting Bugs

1. Check if the issue already exists
2. Create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version)

### Suggesting Features

1. Open an issue with the `enhancement` label
2. Describe the feature and its use case
3. Discuss implementation approach if you have ideas

### Pull Requests

1. **Fork** the repository
2. **Create a branch** for your feature (`git checkout -b feature/amazing-feature`)
3. **Make your changes** following our code style
4. **Test** your changes thoroughly
5. **Commit** with clear messages
6. **Push** to your fork
7. **Open a PR** against `main`

## Development Setup

```bash
# Clone your fork
git clone https://github.com/raullenchai/meridian.git
cd meridian

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run tests (when available)
python -m pytest
```

## Code Style

- **Python**: Follow PEP 8
- **Docstrings**: Google style
- **Type hints**: Use them for function signatures
- **Line length**: 100 characters max
- **Imports**: Group into standard library, third-party, local

```python
# Good example
def extract_topics(posts_text: str, count: int = 10) -> List[Topic]:
    """
    Extract top N important topics from posts.

    Args:
        posts_text: Text containing all Reddit post titles
        count: Number of topics to extract

    Returns:
        List of Topic objects sorted by importance
    """
    pass
```

## Adding a New Source

To add a new data source (e.g., Hacker News, Twitter):

1. Create `modules/your_source_collector.py`
2. Implement the collector following this pattern:

```python
"""
Your Source Collector
Brief description of the source
"""
from dataclasses import dataclass
from typing import List

@dataclass
class Post:
    title: str
    score: int
    url: str
    source: str

def collect_posts(limit: int = 50) -> List[Post]:
    """Collect posts from your source."""
    # Implementation
    pass

def posts_to_text(posts: List[Post]) -> str:
    """Convert posts to text for Claude analysis."""
    # Implementation
    pass
```

3. Register in `main.py` and `config.py`
4. Add tests
5. Update README

## Commit Messages

Use clear, descriptive commit messages:

```
Add Hacker News source collector

- Implement HN API integration
- Add rate limiting
- Include top/new/best story types
```

## Questions?

Open an issue or start a discussion. We're happy to help!
