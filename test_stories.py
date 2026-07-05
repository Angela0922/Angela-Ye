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
    child = ChildProfile(name="Lily", age=5, interests=["stories", "animals"])
    for doll in load_characters():
        story = generate_story(child, doll, prefer_ai=False)
        assert story.child_name == "Lily"
        assert story.doll_name == doll.name
        assert len(story.scenes) == 3
        assert "Lily" in story.full_text()
        assert "Apple Park" in story.full_text() or doll.name in story.full_text()
        assert story.moral


def test_doll_recommendation():
    from services.doll_recommender import recommend_doll

    musical_child = ChildProfile(
        name="Sofia",
        age=5,
        interests=["singing", "music", "dancing"],
        personality_traits=["creative"],
    )
    rec = recommend_doll(musical_child)
    assert rec.doll_id == "gwen"

    story_child = ChildProfile(
        name="Noah",
        age=4,
        interests=["books", "bedtime stories"],
        bedtime_challenge="needs a cozy routine before sleep",
    )
    rec = recommend_doll(story_child)
    assert rec.doll_id == "wren"
    assert rec.reason


def test_chatbot_collects_profile():
    from services.chatbot import create_session, process_message

    session = create_session()
    session, reply, _ = process_message(session, "My daughter's name is Emma and she is 6")
    assert session.profile.name == "Emma"
    assert session.profile.age == 6

    session, reply, _ = process_message(session, "She loves animals and exploring nature")
    assert session.recommendation is not None or "Emma" in reply


def test_story_includes_child_name():
    child = ChildProfile(name="Milo", age=4)
    for doll in load_characters():
        story = generate_story(child, doll, prefer_ai=False)
        assert "Milo" in story.full_text()
        assert story.child_name == "Milo"


def test_create_session_with_name():
    from services.chatbot import create_session

    session = create_session("Emma")
    assert session.profile.name == "Emma"
    assert "Emma" in session.messages[0].content


if __name__ == "__main__":
    test_characters_load()
    test_child_name_validation()
    test_story_generation_all_characters()
    test_doll_recommendation()
    test_chatbot_collects_profile()
    test_story_includes_child_name()
    test_create_session_with_name()
    print("All tests passed.")
