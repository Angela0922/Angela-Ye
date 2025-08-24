# TikTok ES->EN Translator with Neutral Makeup Restyle

This app converts Spanish-language short e-commerce videos into English by:
- Transcribing Spanish speech and translating to English
- Generating English subtitles (SRT)
- Optionally producing an English voiceover dub
- Optionally applying a neutral, mainstream "soft glam" makeup restyle (not tied to any ethnicity)

Important: We do not perform or accept requests to change facial appearance based on protected characteristics (e.g., race, ethnicity). The makeup feature is a neutral style enhancement.

## Setup

Prerequisites:
- Python 3.10+
- FFmpeg installed and on your PATH (`ffmpeg -version`)

Install dependencies:

```bash
python -m venv .venv && source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Usage

Basic pipeline (subtitles only):

```bash
python cli.py \
  --input path/to/tiktok.mp4 \
  --out-dir out \
  --generate-srt
```

Add English dub (simple TTS):

```bash
python cli.py \
  --input path/to/tiktok.mp4 \
  --out-dir out \
  --generate-srt \
  --generate-dub
```

Apply neutral makeup restyle (soft glam preset):

```bash
python cli.py \
  --input path/to/tiktok.mp4 \
  --out-dir out \
  --makeup
```

Combine all:

```bash
python cli.py --input in.mp4 --out-dir out --generate-srt --generate-dub --makeup
```

Outputs:
- `out/transcript_en.srt` — English subtitles
- `out/dub_en.wav` — English TTS dub (approximate)
- `out/video_en.mp4` — Video with replaced audio if dub selected; original audio otherwise
- `out/video_makeup.mp4` — Video with neutral makeup restyle; audio preserved

## Notes
- ASR+translation uses faster-whisper. Set `--whisper-model` to control speed/quality (`tiny`, `base`, `small`, `medium`, `large-v3`).
- TTS uses `pyttsx3` (system voices). Quality varies by system. For higher quality, integrate a neural TTS engine.
- Subtitle burn-in can be added later via FFmpeg if desired.
- For long videos or multiple faces, performance will vary. GPU-accelerated environments will be faster.
