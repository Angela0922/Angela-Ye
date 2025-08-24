#!/usr/bin/env python3
import argparse
import os
import sys
from pathlib import Path

from app.asr import transcribe_spanish_to_english
from app.subtitles import write_srt
from app.tts import synthesize_tts_pyttsx3
from app.video import extract_wav_mono_16k, replace_audio_track
from app.makeup import apply_neutral_makeup_to_video


def main():
	parser = argparse.ArgumentParser(description="Spanish->English translator with neutral makeup restyle")
	parser.add_argument("--input", required=True, help="Path to input video file")
	parser.add_argument("--out-dir", required=True, help="Output directory")
	parser.add_argument("--whisper-model", default="small", help="faster-whisper model size or path (tiny/base/small/medium/large-v3)")
	parser.add_argument("--generate-srt", action="store_true", help="Generate English SRT subtitles")
	parser.add_argument("--generate-dub", action="store_true", help="Generate English TTS dub and replace audio")
	parser.add_argument("--makeup", action="store_true", help="Apply neutral soft-glam makeup restyle (not ethnicity-based)")
	parser.add_argument("--makeup-intensity", type=float, default=0.6, help="Makeup intensity 0..1")
	args = parser.parse_args()

	in_path = Path(args.input)
	out_dir = Path(args.out_dir)
	out_dir.mkdir(parents=True, exist_ok=True)

	if not in_path.exists():
		print(f"Input not found: {in_path}", file=sys.stderr)
		sys.exit(1)

	# 1) Extract audio for ASR
	audio_wav = out_dir / "audio_16k_mono.wav"
	extract_wav_mono_16k(str(in_path), str(audio_wav))

	# 2) Transcribe+translate to English
	segments, full_text = transcribe_spanish_to_english(str(audio_wav), model_size=args.whisper_model)

	# 3) Optionally write SRT
	if args.generate_srt:
		srt_path = out_dir / "transcript_en.srt"
		write_srt(segments, str(srt_path))
		print(f"Wrote SRT: {srt_path}")

	# 4) Optionally TTS dub and replace audio
	output_video_path = out_dir / "video_en.mp4"
	if args.generate_dub:
		dub_wav = out_dir / "dub_en.wav"
		synthesize_tts_pyttsx3(full_text, str(dub_wav))
		replace_audio_track(str(in_path), str(dub_wav), str(output_video_path))
		print(f"Wrote dubbed video: {output_video_path}")
	else:
		# Copy original video to output for consistency
		output_video_path = out_dir / "video_en.mp4"
		replace_audio_track(str(in_path), str(audio_wav), str(output_video_path))  # re-mux with original audio to normalize
		print(f"Wrote re-muxed video: {output_video_path}")

	# 5) Optionally apply neutral makeup restyle
	if args.makeup:
		makeup_out = out_dir / "video_makeup.mp4"
		apply_neutral_makeup_to_video(str(output_video_path), str(makeup_out), intensity=args.makeup_intensity)
		print(f"Wrote makeup restyled video: {makeup_out}")


if __name__ == "__main__":
	main()