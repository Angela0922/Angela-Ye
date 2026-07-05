from __future__ import annotations

import json
import os
import re
from typing import Any

from models.schemas import ChatMessage, ChatSession, ChildProfile, DollRecommendation
from services.doll_recommender import extract_interests_from_text, get_recommendation
from services.safety import is_valid_child_name, sanitize_child_name

WELCOME_MESSAGE = (
    "Hi! I'm your Apple Park storyteller. 🍎\n\n"
    "Tell me about your little one — their **name**, **age**, and what makes them special "
    "(favorite things, personality, bedtime routines). I'll find the perfect Apple Park Kids doll "
    "and weave a personalized bedtime story just for them."
)

WELCOME_WITH_NAME = (
    "Hi! I'm your Apple Park storyteller. 🍎\n\n"
    "I already know **{name}** will star in the story! Tell me a bit more — their age, "
    "favorite things, and personality — and I'll find the perfect Apple Park Kids doll friend."
)

FOLLOW_UP_QUESTIONS = [
    "What's your child's first name?",
    "How old are they? (You can skip this if you'd rather not say.)",
    "What do they love most — animals, music, building, stories, or something else?",
    "Anything about bedtime I should know? (fears, routines, favorite snuggle buddies)",
]


def _missing_fields(profile: ChildProfile) -> list[str]:
    missing: list[str] = []
    if not profile.has_name():
        missing.append("name")
    if profile.age is None:
        missing.append("age")
    if not profile.has_personality_info():
        missing.append("personality")
    return missing


def _parse_age(text: str) -> int | None:
    match = re.search(r"\b(\d{1,2})\s*(?:years?\s*old|yo|y\.?o\.?)?\b", text.lower())
    if match:
        age = int(match.group(1))
        if 1 <= age <= 12:
            return age
    return None


def _parse_name(text: str) -> str | None:
    stripped = text.strip()
    if not stripped:
        return None

    patterns = [
        r"(?:name is|named|call (?:him|her|them)|they'?re called)\s+([A-Za-z][A-Za-z'\- ]{0,30})",
        r"^([A-Za-z][A-Za-z'\-]{1,30})$",
        r"^my (?:child|kid|son|daughter|little one)(?:'s name)? is\s+([A-Za-z][A-Za-z'\- ]{0,30})",
    ]
    for pattern in patterns:
        match = re.search(pattern, stripped, re.IGNORECASE)
        if match:
            candidate = sanitize_child_name(match.group(1).split()[0])
            if is_valid_child_name(candidate):
                return candidate

    words = stripped.split()
    if len(words) <= 3:
        candidate = sanitize_child_name(words[0])
        if is_valid_child_name(candidate):
            return candidate
    return None


def _apply_profile_updates(profile: ChildProfile, text: str) -> ChildProfile:
    name = _parse_name(text)
    if name and not profile.has_name():
        profile.name = name

    age = _parse_age(text)
    if age is not None and profile.age is None:
        profile.age = age

    interests = extract_interests_from_text(text)
    for interest in interests:
        if interest not in profile.interests:
            profile.interests.append(interest)

    lowered = text.lower()
    trait_keywords = {
        "curious": "curious",
        "shy": "shy",
        "brave": "brave",
        "creative": "creative",
        "gentle": "gentle",
        "energetic": "energetic",
        "social": "social",
        "kind": "kind",
        "helpful": "helpful",
    }
    for keyword, trait in trait_keywords.items():
        if keyword in lowered and trait not in profile.personality_traits:
            profile.personality_traits.append(trait)

    bedtime_markers = ["bedtime", "sleep", "night", "afraid", "scared", "monster", "dark", "settle"]
    if any(marker in lowered for marker in bedtime_markers):
        profile.bedtime_challenge = text.strip()[:200]

    if len(text.split()) >= 4 and not profile.notes:
        profile.notes = text.strip()[:300]
    elif len(text.split()) >= 4:
        profile.notes = f"{profile.notes} {text.strip()}"[:400]

    if not profile.favorite_things and interests:
        profile.favorite_things = ", ".join(interests[:3])

    return profile


def _scripted_reply(session: ChatSession) -> str:
    profile = session.profile
    missing = _missing_fields(profile)

    if "name" in missing:
        return (
            "I'd love to get started! What is your child's first name? "
            "Once I know their name, it can appear in their very own Apple Park story."
        )

    name = profile.display_name()

    if "age" in missing and "personality" in missing:
        return (
            f"Lovely — {name} sounds wonderful! How old is {name}, "
            f"and what do they love? (For example: dinosaurs, tea parties, building blocks, or cozy story time.)"
        )

    if "personality" in missing:
        return (
            f"What makes {name} unique? Tell me about their favorite activities, "
            f"personality, or anything that would help me pick the perfect Apple Park friend."
        )

    if session.recommendation:
        doll_name = session.recommendation.doll_name
        return (
            f"I found a perfect match for {name}: **{doll_name}**! "
            f"{session.recommendation.reason}\n\n"
            f"Would you like me to create a personalized bedtime story starring {name} and {doll_name}? "
            f"Just say **yes** or **create my story**."
        )

    return (
        f"Thank you! I have a great picture of {name}. "
        f"Let me find the Apple Park Kids doll who matches them best…"
    )


def _openai_chat_turn(session: ChatSession, user_message: str) -> tuple[str, ChildProfile, bool]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")

    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    system_prompt = """You are a warm Apple Park Kids storyteller chatbot for parents.

Your job:
1. Learn about their child through natural conversation (name, age, interests, personality, bedtime context).
2. Ask one friendly follow-up question at a time when information is missing.
3. When you have at least the child's name AND some personality/interests, set ready_to_recommend to true.
4. Keep replies concise (2-4 sentences), warm, and parent-friendly.
5. Mention Apple Park as a magical inclusive park where organic cotton doll friends live.
6. Never ask for sensitive personal data (address, school, full birthday).

Respond ONLY with valid JSON:
{
  "reply": "your message to the parent",
  "profile": {
    "name": "child first name or empty string",
    "age": null or integer 1-12,
    "interests": ["list of strings"],
    "personality_traits": ["list of strings"],
    "bedtime_challenge": "string or null",
    "favorite_things": "short summary or empty",
    "notes": "other relevant parent notes"
  },
  "ready_to_recommend": false
}"""

    history = [{"role": message.role, "content": message.content} for message in session.messages]
    history.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": system_prompt}, *history],
        temperature=0.7,
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content
    if not content:
        raise ValueError("Empty chatbot response")

    payload: dict[str, Any] = json.loads(content)
    profile_data = payload.get("profile", {})

    updated = ChildProfile(
        name=sanitize_child_name(profile_data.get("name", "")) or session.profile.name,
        age=profile_data.get("age", session.profile.age),
        interests=profile_data.get("interests") or session.profile.interests,
        personality_traits=profile_data.get("personality_traits") or session.profile.personality_traits,
        bedtime_challenge=profile_data.get("bedtime_challenge") or session.profile.bedtime_challenge,
        favorite_things=profile_data.get("favorite_things", session.profile.favorite_things),
        notes=profile_data.get("notes", session.profile.notes),
    )

    if updated.name and not is_valid_child_name(updated.name):
        updated.name = session.profile.name

    return payload.get("reply", ""), updated, bool(payload.get("ready_to_recommend"))


def _wants_story(text: str) -> bool:
    lowered = text.lower()
    triggers = [
        "yes",
        "yeah",
        "yep",
        "sure",
        "please",
        "create",
        "story",
        "generate",
        "let's go",
        "lets go",
        "do it",
        "bedtime story",
    ]
    return any(trigger in lowered for trigger in triggers)


def create_session(initial_name: str = "") -> ChatSession:
    session = ChatSession()
    if initial_name:
        cleaned = sanitize_child_name(initial_name)
        if is_valid_child_name(cleaned):
            session.profile.name = cleaned
            session.messages.append(
                ChatMessage(role="assistant", content=WELCOME_WITH_NAME.format(name=session.profile.display_name()))
            )
            return session
    session.messages.append(ChatMessage(role="assistant", content=WELCOME_MESSAGE))
    return session


def process_message(session: ChatSession, user_message: str) -> tuple[ChatSession, str, DollRecommendation | None]:
    user_message = user_message.strip()
    if not user_message:
        return session, "I'm listening — tell me about your little one!", None

    session.messages.append(ChatMessage(role="user", content=user_message))

    if session.phase == "story_ready" and _wants_story(user_message):
        session.phase = "generating_story"
        reply = (
            f"Wonderful! I'm writing a cozy bedtime story for {session.profile.display_name()} "
            f"and {session.recommendation.doll_name if session.recommendation else 'their new friend'}…"
        )
        session.messages.append(ChatMessage(role="assistant", content=reply))
        return session, reply, session.recommendation

    ready_to_recommend = False
    reply = ""

    if os.getenv("OPENAI_API_KEY"):
        try:
            reply, session.profile, ready_to_recommend = _openai_chat_turn(session, user_message)
        except Exception:
            session.profile = _apply_profile_updates(session.profile, user_message)
            ready_to_recommend = session.profile.has_name() and session.profile.has_personality_info()
            reply = _scripted_reply(session)
    else:
        session.profile = _apply_profile_updates(session.profile, user_message)
        ready_to_recommend = session.profile.has_name() and session.profile.has_personality_info()
        reply = _scripted_reply(session)

    if ready_to_recommend and session.recommendation is None:
        session.recommendation = get_recommendation(session.profile)
        session.phase = "recommended"
        doll_name = session.recommendation.doll_name
        reply = (
            f"{reply}\n\n"
            f"I found the perfect Apple Park friend for {session.profile.display_name()}: "
            f"**{doll_name}**! {session.recommendation.reason}\n\n"
            f"Scroll down to see {doll_name}'s picture and shop link. "
            f"When you're ready, say **create my story** and I'll write their bedtime adventure."
        )
        session.phase = "story_ready"

    session.messages.append(ChatMessage(role="assistant", content=reply))
    return session, reply, session.recommendation
