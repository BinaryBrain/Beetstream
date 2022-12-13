from beetsplug.beetstream.utils import path_to_content_type
from flask import send_file, Response

import ffmpeg

def send_raw_file(filePath):
    return send_file(filePath, mimetype=path_to_content_type(filePath))

def transcode_and_stream(filePath, maxBitrate):
    outputStream = (
        ffmpeg
        .input(filePath)
        .output('pipe:', format="mp3", audio_bitrate=maxBitrate * 1000)
        .run_async(pipe_stdout=True)
    )

    return Response(outputStream.stdout, mimetype='audio/mpeg')

def try_to_transcode(filePath, maxBitrate):
    return transcode_and_stream(filePath, maxBitrate)
