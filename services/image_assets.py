from __future__ import annotations

from pathlib import Path

from models.schemas import DollCharacter

ROOT = Path(__file__).resolve().parent.parent


def doll_image_path(doll: DollCharacter) -> Path | None:
    """Return local product image path if available."""
    if doll.image_local:
        path = ROOT / doll.image_local
        if path.exists():
            return path
    return None


def brand_hero_path() -> Path | None:
    path = ROOT / "assets" / "dolls" / "brand-hero.jpg"
    return path if path.exists() else None
