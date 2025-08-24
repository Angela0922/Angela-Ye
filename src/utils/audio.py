import ffmpeg

def extract_audio(video_path: str, output_wav: str):
    (
        ffmpeg.input(video_path)
        .output(output_wav, ac=1, ar='16k')
        .overwrite_output()
        .run(quiet=True)
    )


def replace_audio(video_path: str, audio_path: str, output_path: str):
    (
        ffmpeg.input(video_path)
        .output(audio_path, shortest=None)
    )
    (
        ffmpeg
        .input(video_path)
        .output(audio_path)
    )
    (
        ffmpeg
        .input(video_path)
        .input(audio_path)
        .output(output_path, c_v='copy', c_a='aac')
        .overwrite_output()
        .run(quiet=True)
    )