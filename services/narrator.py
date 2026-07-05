from __future__ import annotations

import hashlib
from pathlib import Path

from gtts import gTTS

AUDIO_DIR = Path(__file__).resolve().parent.parent / "assets" / "audio"


def narration_cache_key(text: str, lang: str = "en") -> str:
    raw = f"{lang}:{text}"
    return hashlib.sha256(raw.encode()).hexdigest()[:20]


def narrate_text(text: str, lang: str = "en", slow: bool = True) -> Path:
    """Generate spoken narration MP3 for scene text."""
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = AUDIO_DIR / f"{narration_cache_key(text, lang)}.mp3"

    if cache_path.exists():
        return cache_path

    tts = gTTS(text=text, lang=lang, slow=slow)
    tts.save(str(cache_path))
    return cache_path
