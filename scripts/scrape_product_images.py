#!/usr/bin/env python3
"""Download product images from appleparkkids.com Shopify API."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = ROOT / "assets" / "dolls"
CHARACTERS_PATH = ROOT / "data" / "characters.json"

COLLECTION_URL = "https://appleparkkids.com/collections/apple-park-kids/products.json?limit=50"

# Map Shopify product handles to our character ids
HANDLE_TO_ID = {
    "park-friends-alex": "alex",
    "organic-best-friends-ella": "ella",
    "grady-in-caramel": "grady",
    "park-friends-gwen": "gwen",
    "levi-in-sage": "levi",
    "luke-in-marine": "luke",
    "mia-in-dusty-rose": "mia",
    "park-friends-paloma": "paloma",
    "apple-park-kids-wren": "wren",
}


def _score_image(src: str, position: int) -> int:
    """Prefer real product photography over AI-generated placeholders."""
    score = 100 - position
    lower = src.lower()
    if "chatgpt" in lower or "dall" in lower:
        score -= 50
    if re.search(r"dsc_|img_\d|\.jpg|\.jpeg", lower):
        score += 30
    return score


def _pick_best_image(images: list[dict]) -> str:
    ranked = sorted(images, key=lambda img: _score_image(img["src"], img.get("position", 99)), reverse=True)
    return ranked[0]["src"]


def _shopify_image_url(src: str, width: int = 600) -> str:
    if "?" in src:
        base = src.split("?")[0]
    else:
        base = src
    return f"{base}?width={width}"


def main() -> None:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    response = httpx.get(COLLECTION_URL, timeout=30, follow_redirects=True)
    response.raise_for_status()
    products = response.json()["products"]

    image_map: dict[str, dict[str, str]] = {}

    for product in products:
        handle = product["handle"]
        char_id = HANDLE_TO_ID.get(handle)
        if not char_id:
            continue

        images = product.get("images", [])
        if not images:
            print(f"  ✗ {char_id}: no images", file=sys.stderr)
            continue

        best_src = _pick_best_image(images)
        download_url = _shopify_image_url(best_src, width=800)
        ext = ".jpg" if ".jpg" in best_src.lower() else ".png"
        local_path = ASSETS_DIR / f"{char_id}{ext}"

        print(f"  → {char_id}: {product['title']}")
        img_response = httpx.get(download_url, timeout=60, follow_redirects=True)
        img_response.raise_for_status()
        local_path.write_bytes(img_response.content)

        image_map[char_id] = {
            "image_url": best_src,
            "image_local": f"assets/dolls/{char_id}{ext}",
        }
        print(f"     saved {local_path} ({len(img_response.content) // 1024} KB)")

    # Also fetch homepage hero / brand image
    try:
        home = httpx.get("https://appleparkkids.com/", timeout=30, follow_redirects=True)
        # Look for og:image
        match = re.search(r'property="og:image"\s+content="([^"]+)"', home.text)
        if match:
            hero_url = match.group(1)
            hero_path = ASSETS_DIR / "brand-hero.jpg"
            hero_dl = _shopify_image_url(hero_url, width=1200)
            hero_bytes = httpx.get(hero_dl, timeout=60).content
            hero_path.write_bytes(hero_bytes)
            image_map["_brand"] = {"image_url": hero_url, "image_local": "assets/dolls/brand-hero.jpg"}
            print(f"  → brand hero saved")
    except Exception as exc:
        print(f"  (brand hero skipped: {exc})")

    # Update characters.json
    with CHARACTERS_PATH.open(encoding="utf-8") as handle:
        characters = json.load(handle)

    for char in characters:
        info = image_map.get(char["id"])
        if info:
            char["image_url"] = info["image_url"]
            char["image_local"] = info["image_local"]

    with CHARACTERS_PATH.open("w", encoding="utf-8") as handle:
        json.dump(characters, handle, indent=2)
        handle.write("\n")

    print(f"\nUpdated {len(image_map)} doll images in {ASSETS_DIR}")


if __name__ == "__main__":
    main()
