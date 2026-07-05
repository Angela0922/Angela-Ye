from __future__ import annotations

import re

BLOCKED_PATTERNS = [
    r"\b(kill|murder|blood|weapon|gun|knife)\b",
    r"\b(scary monster|nightmare demon|horror)\b",
]

CHILD_NAME_PATTERN = re.compile(r"^[a-zA-Z][a-zA-Z\s'\-]{0,30}[a-zA-Z]?$")


def sanitize_child_name(name: str) -> str:
    cleaned = re.sub(r"[^\w\s'\-]", "", name.strip())
    return cleaned[:32]


def is_valid_child_name(name: str) -> bool:
    cleaned = sanitize_child_name(name)
    if len(cleaned) < 2:
        return False
    return bool(CHILD_NAME_PATTERN.match(cleaned))


def is_story_safe(text: str) -> bool:
    lowered = text.lower()
    return not any(re.search(pattern, lowered) for pattern in BLOCKED_PATTERNS)
