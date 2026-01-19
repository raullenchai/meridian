"""
Meridian - Data Models
"""
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Topic:
    """Represents an extracted AI topic with metadata and generated content."""
    title: str
    title_en: str
    description: str
    keywords: List[str] = field(default_factory=list)
    importance: int = 5
    image_prompt: Optional[str] = None
    image_path: Optional[str] = None
    image_filename: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Topic":
        """Create a Topic from a dictionary (e.g., from Claude's JSON response)."""
        return cls(
            title=data.get("title", "Unknown Topic"),
            title_en=data.get("title_en", data.get("title", "Unknown Topic")),
            description=data.get("description", ""),
            keywords=data.get("keywords", []),
            importance=min(int(data.get("importance", 5)), 10),
            image_prompt=data.get("image_prompt"),
            image_path=data.get("image_path"),
            image_filename=data.get("image_filename"),
        )

    def to_dict(self) -> dict:
        """Convert Topic to dictionary."""
        return {
            "title": self.title,
            "title_en": self.title_en,
            "description": self.description,
            "keywords": self.keywords,
            "importance": self.importance,
            "image_prompt": self.image_prompt,
            "image_path": self.image_path,
            "image_filename": self.image_filename,
        }
