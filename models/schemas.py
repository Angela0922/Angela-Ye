from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DollCharacter:
    id: str
    name: str
    tagline: str
    personality: list[str]
    world: str
    themes: list[str]
    age_range: str
    voice_style: str
    colors: dict[str, str]
    emoji: str
    price: float
    purchase_url: str
    appearance: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DollCharacter:
        return cls(**data)


@dataclass
class ChildProfile:
    name: str
    age: int | None = None

    def display_name(self) -> str:
        cleaned = self.name.strip()
        return cleaned[:1].upper() + cleaned[1:] if cleaned else "Your Child"


@dataclass
class StoryScene:
    title: str
    text: str
    illustration_caption: str


@dataclass
class BedtimeStory:
    title: str
    child_name: str
    doll_name: str
    doll_id: str
    scenes: list[StoryScene] = field(default_factory=list)
    moral: str = ""
    reading_time_minutes: int = 3
    generated_by: str = "template"
    video_path: str | None = None

    def full_text(self) -> str:
        parts = [self.title, ""]
        for scene in self.scenes:
            parts.append(scene.title)
            parts.append(scene.text)
            parts.append("")
        if self.moral:
            parts.append(f"Sweet dreams, {self.child_name}. {self.moral}")
        return "\n".join(parts).strip()
