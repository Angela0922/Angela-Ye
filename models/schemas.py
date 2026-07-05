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
    image_url: str = ""
    image_local: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DollCharacter:
        known = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in known}
        return cls(**filtered)


@dataclass
class ChildProfile:
    name: str = ""
    age: int | None = None
    interests: list[str] = field(default_factory=list)
    personality_traits: list[str] = field(default_factory=list)
    bedtime_challenge: str | None = None
    favorite_things: str = ""
    notes: str = ""

    def display_name(self) -> str:
        cleaned = self.name.strip()
        return cleaned[:1].upper() + cleaned[1:] if cleaned else "Your Child"

    def has_name(self) -> bool:
        return bool(self.name.strip())

    def has_personality_info(self) -> bool:
        return bool(
            self.interests
            or self.personality_traits
            or self.favorite_things.strip()
            or self.bedtime_challenge
            or self.notes.strip()
        )


@dataclass
class DollRecommendation:
    doll_id: str
    doll_name: str
    reason: str
    match_score: float = 0.0
    alternate_ids: list[str] = field(default_factory=list)


@dataclass
class ChatMessage:
    role: str
    content: str


@dataclass
class ChatSession:
    messages: list[ChatMessage] = field(default_factory=list)
    profile: ChildProfile = field(default_factory=ChildProfile)
    phase: str = "greeting"
    recommendation: DollRecommendation | None = None
    story: BedtimeStory | None = None


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
