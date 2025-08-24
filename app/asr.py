from typing import List, Tuple

from faster_whisper import WhisperModel


class TranscriptSegment:
	"""Represents a single transcript segment with timing and English text."""

	def __init__(self, start: float, end: float, text: str) -> None:
		self.start = float(start)
		self.end = float(end)
		self.text = text.strip()

	def __repr__(self) -> str:
		return f"TranscriptSegment(start={self.start:.2f}, end={self.end:.2f}, text={self.text!r})"


def transcribe_spanish_to_english(audio_path: str, model_size: str = "small", compute_type: str = "int8") -> Tuple[List[TranscriptSegment], str]:
	"""Transcribe Spanish audio and translate to English.

	Args:
		audio_path: Path to a mono 16kHz WAV.
		model_size: faster-whisper model name or path.
		compute_type: precision for inference ('int8', 'int8_float16', 'float16', 'float32').

	Returns:
		segments: List of English segments with timestamps.
		full_text: Full English transcript.
	"""
	model = WhisperModel(model_size, device="auto", compute_type=compute_type)
	segments_iter, _info = model.transcribe(
		audio_path,
		language="es",
		task="translate",
		vad_filter=True,
	)

	segments: List[TranscriptSegment] = []
	all_text_parts: List[str] = []
	for seg in segments_iter:
		english_text = (seg.text or "").strip()
		segments.append(TranscriptSegment(seg.start, seg.end, english_text))
		if english_text:
			all_text_parts.append(english_text)

	full_text = " ".join(all_text_parts)
	return segments, full_text