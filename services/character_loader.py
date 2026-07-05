from __future__ import annotations

import json
from pathlib import Path

from models.schemas import DollCharacter

CHARACTERS_PATH = Path(__file__).resolve().parent.parent / "data" / "characters.json"


def load_characters() -> list[DollCharacter]:
    with CHARACTERS_PATH.open(encoding="utf-8") as handle:
        raw = json.load(handle)
    return [DollCharacter.from_dict(item) for item in raw]


def get_character(character_id: str) -> DollCharacter | None:
    for character in load_characters():
        if character.id == character_id:
            return character
    return None
