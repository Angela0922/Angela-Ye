from typing import List
import datetime as dt
import srt

from app.asr import TranscriptSegment


def write_srt(segments: List[TranscriptSegment], srt_path: str) -> None:
	"""Write segments to an SRT file."""
	items: List[srt.Subtitle] = []
	for i, seg in enumerate(segments, start=1):
		start_td = dt.timedelta(seconds=float(seg.start))
		end_td = dt.timedelta(seconds=float(seg.end))
		items.append(srt.Subtitle(index=i, start=start_td, end=end_td, content=seg.text))

	with open(srt_path, "w", encoding="utf-8") as f:
		f.write(srt.compose(items))