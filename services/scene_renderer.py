from __future__ import annotations

import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from models.schemas import BedtimeStory, DollCharacter, StoryScene
from services.image_assets import doll_image_path

SCENES_DIR = Path(__file__).resolve().parent.parent / "assets" / "scene_slides"
WIDTH, HEIGHT = 1280, 720
ROOT = Path(__file__).resolve().parent.parent


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


def _load_doll_photo(doll: DollCharacter, max_height: int = 420) -> Image.Image | None:
    path = doll_image_path(doll)
    if not path:
        return None
    try:
        photo = Image.open(path).convert("RGBA")
        ratio = max_height / photo.height
        new_size = (int(photo.width * ratio), max_height)
        return photo.resize(new_size, Image.Resampling.LANCZOS)
    except Exception:
        return None


def _paste_doll_photo(canvas: Image.Image, doll: DollCharacter, right_margin: int = 40, max_height: int = 420) -> None:
    photo = _load_doll_photo(doll, max_height=max_height)
    if photo is None:
        return
    x = WIDTH - photo.width - right_margin
    y = (HEIGHT - photo.height) // 2 - 20
    # Soft white backdrop behind doll
    backdrop = Image.new("RGBA", (photo.width + 40, photo.height + 40), (255, 255, 255, 60))
    canvas.paste(backdrop, (x - 20, y - 20), backdrop)
    canvas.paste(photo, (x, y), photo)


def render_scene_slide(
    story: BedtimeStory,
    scene: StoryScene,
    doll: DollCharacter,
    scene_index: int,
    output_path: Path,
) -> Path:
    """Render a story scene as a 1280x720 slide image."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    image = Image.new("RGBA", (WIDTH, HEIGHT), doll.colors["secondary"])
    draw = ImageDraw.Draw(image)
    _gradient_background(draw, image, doll.colors["primary"], doll.colors["secondary"])

    badge_font = _load_font(22)
    draw.rounded_rectangle([(40, 30), (280, 70)], radius=12, fill=(255, 255, 255))
    draw.text((55, 38), "Apple Park Kids", fill=_hex_to_rgb(doll.colors["primary"]), font=badge_font)

    title_font = _load_font(36, bold=True)
    draw.text((60, 100), scene.title, fill=(255, 255, 255), font=title_font)

    body_font = _load_font(24)
    wrapped = textwrap.fill(scene.text, width=38)
    draw.multiline_text((60, 170), wrapped, fill=(255, 255, 255), font=body_font, spacing=8)

    _paste_doll_photo(image, doll, max_height=460)

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

    image.convert("RGB").save(output_path, "PNG")
    return output_path


def render_title_slide(story: BedtimeStory, doll: DollCharacter, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    image = Image.new("RGBA", (WIDTH, HEIGHT), doll.colors["secondary"])
    draw = ImageDraw.Draw(image)
    _gradient_background(draw, image, doll.colors["primary"], doll.colors["accent"])

    title_font = _load_font(46, bold=True)
    sub_font = _load_font(28)

    draw.text((60, 180), story.title, fill=(255, 255, 255), font=title_font)
    draw.text((60, 280), f"A bedtime story for {story.child_name}", fill=(255, 255, 255), font=sub_font)
    draw.text((60, 330), "Apple Park Kids · Organic Cotton Dolls", fill=(255, 255, 255), font=_load_font(22))

    _paste_doll_photo(image, doll, max_height=500)

    image.convert("RGB").save(output_path, "PNG")
    return output_path


def render_end_slide(story: BedtimeStory, doll: DollCharacter, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    image = Image.new("RGBA", (WIDTH, HEIGHT), doll.colors["secondary"])
    draw = ImageDraw.Draw(image)
    _gradient_background(draw, image, doll.colors["accent"], doll.colors["primary"])

    title_font = _load_font(38, bold=True)
    body_font = _load_font(24)

    draw.text((60, 200), "Sweet dreams,", fill=(255, 255, 255), font=title_font)
    draw.text((60, 250), story.child_name, fill=(255, 255, 255), font=_load_font(50, bold=True))

    moral = textwrap.fill(story.moral, width=36)
    draw.multiline_text((60, 330), moral, fill=(255, 255, 255), font=body_font, spacing=8)

    draw.text((60, HEIGHT - 80), f"Bring {doll.name} home — ${doll.price:.0f}", fill=(255, 255, 255), font=_load_font(26, bold=True))

    _paste_doll_photo(image, doll, max_height=440)

    image.convert("RGB").save(output_path, "PNG")
    return output_path
