from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from pathlib import Path

ROOT = Path(__file__).resolve().parent

from models.schemas import ChildProfile
from services.character_loader import load_characters
from services.safety import is_valid_child_name, sanitize_child_name
from services.story_generator import generate_story


def test_characters_load():
    characters = load_characters()
    assert len(characters) == 9
    names = {c.name for c in characters}
    assert names == {"Alex", "Ella", "Grady", "Gwen", "Levi", "Luke", "Mia", "Paloma", "Wren"}
    assert all(c.price == 55.0 for c in characters)
    assert all(c.purchase_url.startswith("https://appleparkkids.com") for c in characters)
    assert all(c.image_local for c in characters)
    for doll in characters:
        path = ROOT / doll.image_local
        assert path.exists(), f"Missing image for {doll.id}: {path}"


def test_child_name_validation():
    assert is_valid_child_name("Emma")
    assert is_valid_child_name("Mary-Jane")
    assert not is_valid_child_name("A")
    assert not is_valid_child_name("123")
    assert sanitize_child_name("  Emma!  ") == "Emma"


def test_story_generation_all_characters():
    child = ChildProfile(name="Lily", age=5)
    for doll in load_characters():
        story = generate_story(child, doll, prefer_ai=False)
        assert story.child_name == "Lily"
        assert story.doll_name == doll.name
        assert len(story.scenes) == 3
        assert "Lily" in story.full_text()
        assert "Apple Park" in story.full_text() or doll.name in story.full_text()
        assert story.moral


if __name__ == "__main__":
    test_characters_load()
    test_child_name_validation()
    test_story_generation_all_characters()
    print("All tests passed.")
