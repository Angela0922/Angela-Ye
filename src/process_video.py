import argparse
import os
from pathlib import Path

from utils.audio import extract_audio, replace_audio
from utils.transcribe import transcribe_audio
from utils.translate import translate_text
from utils.tts import text_to_speech
from utils.video_face import process_video_faces


def main():
    parser = argparse.ArgumentParser(description="Translate Spanish TikTok video & change makeup style")
    parser.add_argument("--input", required=True, help="Path to input video")
    parser.add_argument("--output", required=True, help="Path to output video")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    temp_audio = Path("data/temp_audio.wav")

    # 1. Extract audio
    extract_audio(str(input_path), str(temp_audio))

    # 2. Transcribe Spanish audio to text
    spanish_text = transcribe_audio(str(temp_audio))

    # 3. Translate text to English
    english_text = translate_text(spanish_text)

    # 4. Convert translated text to speech
    tts_audio = Path("data/tts_en.wav")
    text_to_speech(english_text, str(tts_audio))

    # 5. Process video frames, apply makeup transfer
    processed_video = Path("data/processed_video.mp4")
    process_video_faces(str(input_path), str(processed_video))

    # 6. Replace audio track with TTS audio
    replace_audio(str(processed_video), str(tts_audio), str(output_path))
    print(f"Saved output video to {output_path}")


if __name__ == "__main__":
    main()