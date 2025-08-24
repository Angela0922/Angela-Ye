import subprocess
import shlex
import os


def _run_ffmpeg(cmd: str) -> None:
	"""Run an ffmpeg command string, raising on error."""
	print(f"[ffmpeg] {cmd}")
	proc = subprocess.run(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
	if proc.returncode != 0:
		raise RuntimeError(proc.stdout.decode("utf-8", errors="ignore"))


def extract_wav_mono_16k(input_video: str, out_wav: str) -> None:
	os.makedirs(os.path.dirname(os.path.abspath(out_wav)), exist_ok=True)
	cmd = (
		f"ffmpeg -y -i {shlex.quote(input_video)} -ac 1 -ar 16000 -vn -c:a pcm_s16le {shlex.quote(out_wav)}"
	)
	_run_ffmpeg(cmd)


def replace_audio_track(input_video: str, new_audio_wav: str, output_video: str) -> None:
	os.makedirs(os.path.dirname(os.path.abspath(output_video)), exist_ok=True)
	cmd = (
		f"ffmpeg -y -i {shlex.quote(input_video)} -i {shlex.quote(new_audio_wav)} "
		f"-map 0:v:0 -map 1:a:0 -c:v libx264 -preset veryfast -crf 20 -shortest {shlex.quote(output_video)}"
	)
	_run_ffmpeg(cmd)