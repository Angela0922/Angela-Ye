from __future__ import annotations

import json
import os
import random
from pathlib import Path
from typing import Any

from models.schemas import BedtimeStory, ChildProfile, DollCharacter, StoryScene
from services.safety import is_story_safe

MIN_NAME_MENTIONS = 2


def story_mentions_child(story: BedtimeStory, child_name: str) -> bool:
    if not child_name.strip():
        return False
    text = story.full_text()
    return text.lower().count(child_name.lower()) >= MIN_NAME_MENTIONS

TEMPLATES_PATH = Path(__file__).resolve().parent.parent / "data" / "story_templates.json"


def _load_templates() -> dict[str, list[dict[str, str]]]:
    with TEMPLATES_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def _format_template(template: dict[str, str], child: ChildProfile, doll: DollCharacter) -> BedtimeStory:
    child_name = child.display_name()
    context = {"child": child_name, "doll": doll.name, "park": "Apple Park"}

    def fmt(value: str) -> str:
        return value.format(**context)

    scenes = [
        StoryScene(
            title=fmt(template["scene_1_title"]),
            text=fmt(template["scene_1"]),
            illustration_caption=fmt(template["scene_1_caption"]),
        ),
        StoryScene(
            title=fmt(template["scene_2_title"]),
            text=fmt(template["scene_2"]),
            illustration_caption=fmt(template["scene_2_caption"]),
        ),
        StoryScene(
            title=fmt(template["scene_3_title"]),
            text=fmt(template["scene_3"]),
            illustration_caption=fmt(template["scene_3_caption"]),
        ),
    ]

    return BedtimeStory(
        title=fmt(template["title"]),
        child_name=child_name,
        doll_name=doll.name,
        doll_id=doll.id,
        scenes=scenes,
        moral=fmt(template["moral"]),
        reading_time_minutes=3,
        generated_by="template",
    )


def generate_template_story(child: ChildProfile, doll: DollCharacter) -> BedtimeStory:
    templates = _load_templates()
    doll_templates = templates.get(doll.id)
    if not doll_templates:
        raise ValueError(f"No story template for doll: {doll.id}")
    template = random.choice(doll_templates)
    return _format_template(template, child, doll)


def _build_llm_prompt(child: ChildProfile, doll: DollCharacter) -> str:
    age_note = f"They are {child.age} years old." if child.age else ""
    interests_note = ""
    if child.interests:
        interests_note = f"Interests: {', '.join(child.interests)}."
    traits_note = ""
    if child.personality_traits:
        traits_note = f"Personality: {', '.join(child.personality_traits)}."
    bedtime_note = ""
    if child.bedtime_challenge:
        bedtime_note = f"Bedtime context: {child.bedtime_challenge}."
    favorites_note = ""
    if child.favorite_things:
        favorites_note = f"Favorite things: {child.favorite_things}."
    return f"""Write a short, gentle bedtime story for a child named {child.display_name()}. {age_note}
{interests_note} {traits_note} {favorites_note} {bedtime_note}

The story stars "{doll.name}" from Apple Park Kids — an organic cotton doll brand.
Character: {doll.tagline}
Appearance: {doll.appearance}
Personality: {", ".join(doll.personality)}.
World: {doll.world} — a sunny, inclusive park where kids play together.
Themes: {", ".join(doll.themes)}.
Voice style: {doll.voice_style}.

Requirements:
- Use the child's name naturally 4-6 times throughout the story
- Mention Apple Park as the setting
- Exactly 3 short scenes, each 2-3 sentences
- Age-appropriate, calming, no scary content, no violence
- End with a gentle moral and bedtime feeling
- This is a sales preview for the {doll.name} doll ($55 organic cotton doll)

Respond ONLY with valid JSON in this exact shape:
{{
  "title": "story title",
  "scenes": [
    {{"title": "scene title", "text": "scene text", "illustration_caption": "short image caption"}},
    {{"title": "...", "text": "...", "illustration_caption": "..."}},
    {{"title": "...", "text": "...", "illustration_caption": "..."}}
  ],
  "moral": "one gentle sentence"
}}"""


def _parse_llm_response(payload: dict[str, Any], child: ChildProfile, doll: DollCharacter) -> BedtimeStory:
    scenes = [
        StoryScene(
            title=scene["title"],
            text=scene["text"],
            illustration_caption=scene.get("illustration_caption", scene["title"]),
        )
        for scene in payload["scenes"]
    ]
    story = BedtimeStory(
        title=payload["title"],
        child_name=child.display_name(),
        doll_name=doll.name,
        doll_id=doll.id,
        scenes=scenes,
        moral=payload.get("moral", ""),
        reading_time_minutes=3,
        generated_by="openai",
    )
    if not is_story_safe(story.full_text()):
        raise ValueError("Generated story failed safety check")
    if not story_mentions_child(story, child.display_name()):
        raise ValueError("Generated story did not include the child's name")
    return story


def generate_openai_story(child: ChildProfile, doll: DollCharacter) -> BedtimeStory:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")

    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError("openai package not installed") from exc

    client = OpenAI(api_key=api_key)
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You write warm, age-appropriate bedtime stories for children featuring "
                    "Apple Park Kids organic dolls. Always respond with valid JSON only."
                ),
            },
            {"role": "user", "content": _build_llm_prompt(child, doll)},
        ],
        temperature=0.8,
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content
    if not content:
        raise ValueError("Empty response from OpenAI")

    payload = json.loads(content)
    return _parse_llm_response(payload, child, doll)


def swap_child_name_in_story(story: BedtimeStory, new_name: str) -> BedtimeStory:
    """Replace the previous child name everywhere in an existing story."""
    import re

    old_name = story.child_name
    if not new_name.strip() or old_name.lower() == new_name.lower():
        story.child_name = new_name
        return story

    def swap(text: str) -> str:
        if not text:
            return text
        return re.sub(re.escape(old_name), new_name, text, flags=re.IGNORECASE)

    story.title = swap(story.title)
    story.child_name = new_name
    story.scenes = [
        StoryScene(
            title=swap(scene.title),
            text=swap(scene.text),
            illustration_caption=swap(scene.illustration_caption),
        )
        for scene in story.scenes
    ]
    story.moral = swap(story.moral)
    return ensure_child_name_in_story(story, new_name)


def ensure_child_name_in_story(story: BedtimeStory, child_name: str) -> BedtimeStory:
    """Guarantee the child's name appears in the story text."""
    if story_mentions_child(story, child_name):
        return story

    if not story.scenes:
        return story

    first = story.scenes[0]
    story.scenes[0] = StoryScene(
        title=first.title,
        text=f"In Apple Park, {child_name} had the most wonderful adventure. {first.text}",
        illustration_caption=first.illustration_caption,
    )
    if len(story.scenes) > 1 and child_name.lower() not in story.scenes[1].text.lower():
        second = story.scenes[1]
        story.scenes[1] = StoryScene(
            title=second.title,
            text=f"{second.text} {child_name} giggled with delight.",
            illustration_caption=second.illustration_caption,
        )
    story.child_name = child_name
    return story


def regenerate_story_for_child(child: ChildProfile, doll: DollCharacter) -> BedtimeStory:
    """Create a fresh story with the child's name woven throughout."""
    return generate_story(child, doll)


def generate_story(child: ChildProfile, doll: DollCharacter, prefer_ai: bool = True) -> BedtimeStory:
    child_name = child.display_name()
    if prefer_ai and os.getenv("OPENAI_API_KEY"):
        try:
            story = generate_openai_story(child, doll)
            return ensure_child_name_in_story(story, child_name)
        except Exception:
            pass
    story = generate_template_story(child, doll)
    return ensure_child_name_in_story(story, child_name)
