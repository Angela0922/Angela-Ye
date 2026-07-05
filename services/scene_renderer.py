from __future__ import annotations

import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from models.schemas import BedtimeStory, DollCharacter, StoryScene

SCENES_DIR = Path(__file__).resolve().parent.parent / "assets" / "scene_slides"
WIDTH, HEIGHT = 1280, 720


def _load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def _gradient_background(
    draw: ImageDraw.ImageDraw,
    image: Image.Image,
    primary: str,
    secondary: str,
) -> None:
    c1 = _hex_to_rgb(primary)
    c2 = _hex_to_rgb(secondary)
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        color = tuple(int(c1[i] + (c2[i] - c1[i]) * ratio) for i in range(3))
        draw.line([(0, y), (WIDTH, y)], fill=color)
    del image  # draw operates in-place on image pixels via line


def render_scene_slide(
    story: BedtimeStory,
    scene: StoryScene,
    doll: DollCharacter,
    scene_index: int,
    output_path: Path,
) -> Path:
    """Render a story scene as a 1280x720 slide image."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    image = Image.new("RGB", (WIDTH, HEIGHT), doll.colors["secondary"])
    draw = ImageDraw.Draw(image)
    _gradient_background(draw, image, doll.colors["primary"], doll.colors["secondary"])

    # Apple Park badge
    badge_font = _load_font(22)
    draw.rounded_rectangle([(40, 30), (280, 70)], radius=12, fill=(255, 255, 255, 180))
    draw.text((55, 38), "Apple Park Kids", fill=_hex_to_rgb(doll.colors["primary"]), font=badge_font)

    # Character emoji (large)
    emoji_font = _load_font(120)
    draw.text((WIDTH // 2 - 60, 80), doll.emoji, fill=(255, 255, 255), font=emoji_font)

    # Scene title
    title_font = _load_font(42, bold=True)
    title = scene.title
    draw.text((WIDTH // 2, 230), title, fill=(255, 255, 255), font=title_font, anchor="mt")

    # Scene text (wrapped)
    body_font = _load_font(28)
    wrapped = textwrap.fill(scene.text, width=48)
    draw.multiline_text(
        (80, 310),
        wrapped,
        fill=(255, 255, 255),
        font=body_font,
        spacing=10,
    )

    # Caption bar at bottom
    caption_font = _load_font(20)
    accent = _hex_to_rgb(doll.colors["accent"])
    draw.rectangle([(0, HEIGHT - 60), (WIDTH, HEIGHT)], fill=accent)
    draw.text(
        (WIDTH // 2, HEIGHT - 30),
        f"Starring {story.child_name} & {doll.name}  ·  Scene {scene_index + 1}",
        fill=(255, 255, 255),
        font=caption_font,
        anchor="mm",
    )

    image.save(output_path, "PNG")
    return output_path


def render_title_slide(story: BedtimeStory, doll: DollCharacter, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    image = Image.new("RGB", (WIDTH, HEIGHT), doll.colors["secondary"])
    draw = ImageDraw.Draw(image)
    _gradient_background(draw, image, doll.colors["primary"], doll.colors["accent"])

    title_font = _load_font(52, bold=True)
    sub_font = _load_font(30)
    emoji_font = _load_font(100)

    draw.text((WIDTH // 2, 200), doll.emoji, fill=(255, 255, 255), font=emoji_font, anchor="mm")
    draw.text((WIDTH // 2, 340), story.title, fill=(255, 255, 255), font=title_font, anchor="mm")
    draw.text(
        (WIDTH // 2, 420),
        f"A bedtime story for {story.child_name}",
        fill=(255, 255, 255),
        font=sub_font,
        anchor="mm",
    )
    draw.text(
        (WIDTH // 2, 470),
        "Apple Park Kids · Organic Cotton Dolls",
        fill=(255, 255, 255),
        font=_load_font(22),
        anchor="mm",
    )

    image.save(output_path, "PNG")
    return output_path


def render_end_slide(story: BedtimeStory, doll: DollCharacter, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    image = Image.new("RGB", (WIDTH, HEIGHT), doll.colors["secondary"])
    draw = ImageDraw.Draw(image)
    _gradient_background(draw, image, doll.colors["accent"], doll.colors["primary"])

    title_font = _load_font(40, bold=True)
    body_font = _load_font(26)

    draw.text((WIDTH // 2, 250), "Sweet dreams,", fill=(255, 255, 255), font=title_font, anchor="mm")
    draw.text((WIDTH // 2, 310), story.child_name, fill=(255, 255, 255), font=_load_font(56, bold=True), anchor="mm")

    moral = textwrap.fill(story.moral, width=50)
    draw.multiline_text((120, 400), moral, fill=(255, 255, 255), font=body_font, spacing=8)

    draw.text(
        (WIDTH // 2, HEIGHT - 80),
        f"Bring {doll.name} home — ${doll.price:.0f}",
        fill=(255, 255, 255),
        font=_load_font(28, bold=True),
        anchor="mm",
    )

    image.save(output_path, "PNG")
    return output_path
