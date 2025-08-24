import pyttsx3
import tempfile
import os


def synthesize_tts_pyttsx3(text: str, wav_path: str) -> None:
	"""Synthesize English TTS to WAV using system voices via pyttsx3.

	Note: This uses system TTS engines (e.g., eSpeak). Quality varies by environment.
	"""
	engine = pyttsx3.init()
	# Try to prefer an English voice if available
	try:
		voices = engine.getProperty("voices")
		for v in voices:
			if "en_" in (v.id or "") or "English" in (v.name or ""):
				engine.setProperty("voice", v.id)
				break
	except Exception:
		pass

	# pyttsx3 save_to_file requires a file; ensure directory exists
	os.makedirs(os.path.dirname(os.path.abspath(wav_path)), exist_ok=True)
	engine.save_to_file(text, wav_path)
	engine.runAndWait()