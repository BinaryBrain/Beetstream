from beetsplug.beetstream.utils import path_to_content_type
from flask import send_file, Response

import importlib
have_ffmpeg = importlib.util.find_spec("ffmpeg") is not None

if have_ffmpeg:
    import ffmpeg

def send_raw_file(filePath):
    return send_file(filePath, mimetype=path_to_content_type(filePath))

def transcode_and_stream(filePath, maxBitrate):
    if not have_ffmpeg:
        raise RuntimeError("Can't transcode, ffmpeg-python is not available")

    outputStream = (
        ffmpeg
        .input(filePath)
        .audio
        .output('pipe:', format="mp3", audio_bitrate=maxBitrate * 1000)
        .run_async(pipe_stdout=True, quiet=True)
    )

    return Response(outputStream.stdout, mimetype='audio/mpeg')

def try_to_transcode(filePath, maxBitrate):
    if have_ffmpeg:
        return transcode_and_stream(filePath, maxBitrate)
    else:
        return send_raw_file(filePath)
