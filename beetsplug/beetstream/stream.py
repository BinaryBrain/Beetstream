from beetsplug.beetstream.utils import path_to_content_type
from flask import Response

def stream(filePath, maxBitrate):
    def generate():
        with open(filePath, "rb") as songFile:
            data = songFile.read(1024)
            while data:
                yield data
                data = songFile.read(1024)

    return Response(generate(), mimetype=path_to_content_type(filePath.decode('utf-8')))
