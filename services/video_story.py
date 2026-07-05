from __future__ import annotations

import hashlib
import shutil
import subprocess
import tempfile
from pathlib import Path

from models.schemas import BedtimeStory, DollCharacter
from services.narrator import narrate_text
from services.scene_renderer import render_end_slide, render_scene_slide, render_title_slide

VIDEOS_DIR = Path(__file__).resolve().parent.parent / "assets" / "videos"
FFMPEG = shutil.which("ffmpeg") or "ffmpeg"


def video_cache_key(story: BedtimeStory) -> str:
    scene_text = "|".join(s.text for s in story.scenes)
    raw = f"{story.doll_id}:{story.child_name}:{story.title}:{scene_text}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def get_video_path(story: BedtimeStory) -> Path | None:
    path = VIDEOS_DIR / f"{video_cache_key(story)}.mp4"
    return path if path.exists() else None


def _image_duration(audio_path: Path, min_seconds: float = 4.0) -> float:
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "error", "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1", str(audio_path),
            ],
            capture_output=True, text=True, check=True,
        )
        duration = float(result.stdout.strip())
        return max(duration + 0.5, min_seconds)
    except Exception:
        return min_seconds


def _make_segment(image: Path, audio: Path | None, duration: float, output: Path) -> None:
    if audio and audio.exists():
        subprocess.run(
            [
                FFMPEG, "-y",
                "-loop", "1", "-i", str(image),
                "-i", str(audio),
                "-c:v", "libx264", "-tune", "stillimage",
                "-c:a", "aac", "-b:a", "128k",
                "-pix_fmt", "yuv420p",
                "-shortest",
                "-t", str(duration + 1),
                str(output),
            ],
            check=True, capture_output=True,
        )
    else:
        subprocess.run(
            [
                FFMPEG, "-y",
                "-loop", "1", "-i", str(image),
                "-c:v", "libx264", "-tune", "stillimage",
                "-pix_fmt", "yuv420p",
                "-t", str(duration),
                str(output),
            ],
            check=True, capture_output=True,
        )


def generate_video_story(story: BedtimeStory, doll: DollCharacter) -> Path:
    """Build an MP4 video story with narrated scene slides."""
    cached = get_video_path(story)
    if cached:
        return cached

    VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = VIDEOS_DIR / f"{video_cache_key(story)}.mp4"
    cache_id = video_cache_key(story)
    slides_dir = Path(tempfile.mkdtemp(prefix=f"apks_{cache_id}_"))

    try:
        segments: list[Path] = []

        # Title card (3 sec, no narration)
        title_img = render_title_slide(story, doll, slides_dir / "00_title.png")
        title_seg = slides_dir / "seg_00.mp4"
        _make_segment(title_img, None, 3.0, title_seg)
        segments.append(title_seg)

        # Scene slides with narration
        for index, scene in enumerate(story.scenes):
            slide_img = render_scene_slide(
                story, scene, doll, index, slides_dir / f"scene_{index + 1}.png"
            )
            narration = scene.text
            if index == 0:
                narration = f"{scene.title}. {scene.text}"
            audio_path = narrate_text(narration)
            duration = _image_duration(audio_path)
            seg_path = slides_dir / f"seg_{index + 1}.mp4"
            _make_segment(slide_img, audio_path, duration, seg_path)
            segments.append(seg_path)

        # End card with moral narration
        end_img = render_end_slide(story, doll, slides_dir / "99_end.png")
        moral_text = f"Sweet dreams, {story.child_name}. {story.moral}"
        moral_audio = narrate_text(moral_text)
        end_seg = slides_dir / "seg_end.mp4"
        _make_segment(end_img, moral_audio, _image_duration(moral_audio, 5.0), end_seg)
        segments.append(end_seg)

        # Concatenate all segments
        concat_list = slides_dir / "concat.txt"
        concat_list.write_text("\n".join(f"file '{s}'" for s in segments))

        subprocess.run(
            [
                FFMPEG, "-y", "-f", "concat", "-safe", "0",
                "-i", str(concat_list),
                "-c", "copy",
                str(output_path),
            ],
            check=True, capture_output=True,
        )

        return output_path
    finally:
        shutil.rmtree(slides_dir, ignore_errors=True)
