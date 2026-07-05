#!/usr/bin/env python3
"""Pre-generate default video stories for every Apple Park Kids doll.

Usage:
    python3 scripts/generate_all_videos.py
    python3 scripts/generate_all_videos.py --child-name Emma
"""

from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models.schemas import ChildProfile
from services.character_loader import load_characters
from services.story_generator import generate_story
from services.video_story import generate_video_story


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate video stories for all Apple Park Kids dolls")
    parser.add_argument("--child-name", default="Friend", help="Child name to personalize stories with")
    parser.add_argument("--age", type=int, default=5, help="Child age")
    parser.add_argument("--no-ai", action="store_true", help="Use template stories only")
    args = parser.parse_args()

    child = ChildProfile(name=args.child_name, age=args.age)
    characters = load_characters()

    print(f"Generating video stories for {len(characters)} Apple Park Kids dolls...")
    print(f"Personalized for: {child.display_name()}\n")

    for doll in characters:
        print(f"  → {doll.name}...", end=" ", flush=True)
        try:
            story = generate_story(child, doll, prefer_ai=not args.no_ai)
            video_path = generate_video_story(story, doll)
            print(f"✓ {video_path}")
        except Exception as exc:
            print(f"✗ {exc}")

    print("\nDone! Videos saved to assets/videos/")


if __name__ == "__main__":
    main()
