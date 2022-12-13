from beetsplug.beetstream.utils import path_to_content_type
from flask import send_file, Response

def send_raw_file(filePath):
    return send_file(filePath, mimetype=path_to_content_type(filePath))

def stream(filePath, maxBitrate):
    return send_raw_file(filePath)
