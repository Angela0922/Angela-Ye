from __future__ import annotations

import hashlib
import os
from pathlib import Path

from models.schemas import BedtimeStory, DollCharacter, StoryScene

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets" / "scenes"


def scene_gradient(doll: DollCharacter, scene_index: int) -> str:
    colors = doll.colors
    primary = colors["primary"]
    secondary = colors["secondary"]
    accent = colors["accent"]
    angle = 135 + (scene_index * 30)
    return (
        f"linear-gradient({angle}deg, {primary} 0%, {secondary} 55%, {accent} 100%)"
    )


def scene_emoji(doll: DollCharacter, scene_index: int) -> str:
    extras = {
        "alex": ["🌳", "🪲", "🍃"],
        "ella": ["🫖", "🧁", "💕"],
        "grady": ["🦸", "🤗", "⭐"],
        "gwen": ["🎵", "🎶", "🌙"],
        "levi": ["🏰", "🏖️", "✨"],
        "luke": ["🎠", "🌤️", "💤"],
        "mia": ["🙈", "😄", "🎁"],
        "paloma": ["🍎", "🤝", "💛"],
        "wren": ["📖", "☕", "🌟"],
    }
    icons = extras.get(doll.id, [doll.emoji, "🍎", "🌙"])
    return icons[scene_index % len(icons)]


def illustration_cache_key(story: BedtimeStory, scene: StoryScene, index: int) -> str:
    raw = f"{story.doll_id}:{story.child_name}:{scene.title}:{index}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def get_scene_image_path(story: BedtimeStory, scene: StoryScene, index: int) -> Path | None:
    key = illustration_cache_key(story, scene, index)
    path = ASSETS_DIR / f"{key}.png"
    return path if path.exists() else None


def generate_scene_image(
    story: BedtimeStory,
    scene: StoryScene,
    doll: DollCharacter,
    index: int,
) -> Path | None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = ASSETS_DIR / f"{illustration_cache_key(story, scene, index)}.png"
    if cache_path.exists():
        return cache_path

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        prompt = (
            f"Children's book illustration, soft watercolor style, warm organic cotton doll aesthetic. "
            f"Apple Park Kids doll character {doll.name} ({doll.appearance or doll.tagline}) "
            f"with a child named {story.child_name} in sunny Apple Park. "
            f"Scene: {scene.illustration_caption}. "
            f"Gentle pastel colors, GOTS organic feel, no text, no scary elements, ages 3-8."
        )
        response = client.images.generate(
            model=os.getenv("OPENAI_IMAGE_MODEL", "dall-e-3"),
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url
        if not image_url:
            return None

        import httpx

        image_bytes = httpx.get(image_url, timeout=60).content
        cache_path.write_bytes(image_bytes)
        return cache_path
    except Exception:
        return None
