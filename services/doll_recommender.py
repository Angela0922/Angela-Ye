from __future__ import annotations

import os
import re
from typing import Any

from models.schemas import ChildProfile, DollCharacter, DollRecommendation
from services.character_loader import load_characters

DOLL_KEYWORDS: dict[str, list[str]] = {
    "alex": [
        "curious",
        "explore",
        "explorer",
        "nature",
        "animal",
        "animals",
        "bug",
        "bugs",
        "outdoor",
        "outdoors",
        "adventure",
        "discover",
        "critter",
        "park",
        "hike",
    ],
    "ella": [
        "social",
        "friend",
        "friends",
        "party",
        "tea",
        "playdate",
        "welcoming",
        "kind",
        "together",
        "sleepover",
        "gather",
    ],
    "grady": [
        "helpful",
        "help",
        "brave",
        "caring",
        "empathy",
        "comfort",
        "hero",
        "support",
        "protect",
        "strong",
    ],
    "gwen": [
        "music",
        "sing",
        "singing",
        "song",
        "dance",
        "creative",
        "art",
        "musical",
        "rhythm",
        "perform",
    ],
    "levi": [
        "build",
        "building",
        "blocks",
        "sandcastle",
        "create",
        "architect",
        "construct",
        "lego",
        "maker",
        "design",
    ],
    "luke": [
        "gentle",
        "calm",
        "playground",
        "easy",
        "patient",
        "soft",
        "peaceful",
        "quiet",
        "sweet",
    ],
    "mia": [
        "shy",
        "peek",
        "peek-a-boo",
        "timid",
        "gentle",
        "soft",
        "cuddly",
        "sensitive",
        "quiet",
        "reserved",
    ],
    "paloma": [
        "share",
        "sharing",
        "kind",
        "generous",
        "give",
        "caring",
        "thoughtful",
        "sweet",
        "helpful",
    ],
    "wren": [
        "story",
        "stories",
        "read",
        "reading",
        "book",
        "books",
        "cozy",
        "bedtime",
        "calm",
        "snuggle",
        "cuddle",
        "imagine",
    ],
}

BEDTIME_KEYWORDS: dict[str, list[str]] = {
    "wren": ["bedtime", "sleep", "story", "cozy", "calm", "night", "afraid of dark", "won't settle"],
    "grady": ["scared", "afraid", "worried", "anxious", "comfort", "brave"],
    "luke": ["hyper", "energetic", "wind down", "calm down", "settle"],
    "mia": ["shy", "new", "nervous", "separation"],
}


def _profile_text(child: ChildProfile) -> str:
    parts = [
        child.name,
        child.favorite_things,
        child.notes,
        child.bedtime_challenge or "",
        " ".join(child.interests),
        " ".join(child.personality_traits),
    ]
    if child.age:
        parts.append(f"age {child.age}")
    return " ".join(parts).lower()


def _score_doll(child: ChildProfile, doll: DollCharacter) -> float:
    text = _profile_text(child)
    if not text.strip():
        return 0.0

    score = 0.0
    keywords = DOLL_KEYWORDS.get(doll.id, [])
    for keyword in keywords:
        if keyword in text:
            score += 2.0

    for trait in doll.personality:
        if trait.lower() in text:
            score += 1.5

    for theme in doll.themes:
        if theme.lower() in text:
            score += 1.0

    bedtime_keywords = BEDTIME_KEYWORDS.get(doll.id, [])
    if child.bedtime_challenge:
        challenge = child.bedtime_challenge.lower()
        for keyword in bedtime_keywords:
            if keyword in challenge or keyword in text:
                score += 2.5

    if child.age:
        age_range = doll.age_range.replace(" ", "")
        if "-" in age_range:
            low, high = age_range.split("-", 1)
            try:
                if int(low) <= child.age <= int(high):
                    score += 0.5
            except ValueError:
                pass

    return score


def _build_reason(child: ChildProfile, doll: DollCharacter) -> str:
    name = child.display_name()
    highlights: list[str] = []

    text = _profile_text(child)
    for trait in doll.personality[:2]:
        if trait.lower() in text:
            highlights.append(trait)

    for theme in doll.themes:
        if theme.lower() in text and theme not in highlights:
            highlights.append(theme)
        if len(highlights) >= 2:
            break

    if highlights:
        trait_text = " and ".join(highlights)
        return (
            f"{doll.name} is a wonderful match for {name} — both love {trait_text}. "
            f"{doll.tagline}."
        )

    if child.bedtime_challenge:
        return (
            f"{doll.name} is a gentle bedtime companion for {name}. "
            f"{doll.tagline}."
        )

    return (
        f"{doll.name} would be a sweet Apple Park friend for {name}. "
        f"{doll.tagline}."
    )


def recommend_doll(child: ChildProfile) -> DollRecommendation:
    characters = load_characters()
    scored = sorted(
        ((doll, _score_doll(child, doll)) for doll in characters),
        key=lambda item: item[1],
        reverse=True,
    )

    best_doll, best_score = scored[0]
    if best_score <= 0:
        best_doll = next((d for d in characters if d.id == "wren"), characters[0])
        best_score = 1.0

    alternates = [doll.id for doll, score in scored[1:3] if score > 0]

    return DollRecommendation(
        doll_id=best_doll.id,
        doll_name=best_doll.name,
        reason=_build_reason(child, best_doll),
        match_score=best_score,
        alternate_ids=alternates,
    )


def _build_llm_recommendation_prompt(child: ChildProfile, characters: list[DollCharacter]) -> str:
    catalog = [
        {
            "id": doll.id,
            "name": doll.name,
            "personality": doll.personality,
            "themes": doll.themes,
            "tagline": doll.tagline,
        }
        for doll in characters
    ]
    return f"""Pick the best Apple Park Kids doll for this child.

Child profile:
- Name: {child.display_name()}
- Age: {child.age or "unknown"}
- Interests: {", ".join(child.interests) or "not specified"}
- Personality: {", ".join(child.personality_traits) or "not specified"}
- Favorite things: {child.favorite_things or "not specified"}
- Bedtime notes: {child.bedtime_challenge or "none"}
- Parent notes: {child.notes or "none"}

Available dolls:
{catalog}

Respond ONLY with valid JSON:
{{
  "doll_id": "one of the doll ids",
  "reason": "2 sentences explaining why this doll fits the child",
  "alternate_ids": ["optional", "second choice ids"]
}}"""


def recommend_doll_with_ai(child: ChildProfile) -> DollRecommendation | None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    try:
        from openai import OpenAI
    except ImportError:
        return None

    characters = load_characters()
    valid_ids = {doll.id for doll in characters}

    client = OpenAI(api_key=api_key)
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You recommend Apple Park Kids organic cotton dolls to parents. "
                    "Always respond with valid JSON only."
                ),
            },
            {"role": "user", "content": _build_llm_recommendation_prompt(child, characters)},
        ],
        temperature=0.4,
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content
    if not content:
        return None

    import json

    payload: dict[str, Any] = json.loads(content)
    doll_id = payload.get("doll_id", "")
    if doll_id not in valid_ids:
        return None

    doll = next(d for d in characters if d.id == doll_id)
    alternates = [item for item in payload.get("alternate_ids", []) if item in valid_ids and item != doll_id]

    return DollRecommendation(
        doll_id=doll_id,
        doll_name=doll.name,
        reason=payload.get("reason", _build_reason(child, doll)),
        match_score=10.0,
        alternate_ids=alternates[:2],
    )


def get_recommendation(child: ChildProfile) -> DollRecommendation:
    ai_result = recommend_doll_with_ai(child)
    if ai_result:
        return ai_result
    return recommend_doll(child)


def extract_interests_from_text(text: str) -> list[str]:
    cleaned = re.sub(r"[^\w\s,\-']", " ", text.lower())
    tokens = [token.strip() for token in re.split(r"[,;]|\band\b", cleaned) if token.strip()]
    stop_words = {"my", "child", "kid", "loves", "likes", "enjoys", "really", "very", "the", "a", "an"}
    results: list[str] = []
    for token in tokens:
        words = [word for word in token.split() if word not in stop_words and len(word) > 2]
        phrase = " ".join(words).strip()
        if phrase and phrase not in results:
            results.append(phrase)
    return results[:8]
