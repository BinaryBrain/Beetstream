from beetsplug.beetstream.utils import *
from beetsplug.beetstream import app
from flask import g, request
from io import BytesIO
from PIL import Image
import flask
import os
import subprocess
import tempfile

@app.route('/rest/getCoverArt', methods=["GET", "POST"])
@app.route('/rest/getCoverArt.view', methods=["GET", "POST"])
def cover_art_file():
    id = request.values.get('id')
    size = request.values.get('size')
    album = None

    if id[:len(ALBUM_ID_PREFIX)] == ALBUM_ID_PREFIX:
        album_id = int(album_subid_to_beetid(id) or -1)
        album = g.lib.get_album(album_id)
    else:
        item_id = int(song_subid_to_beetid(id) or -1)
        item = g.lib.get_item(item_id)

        if item is not None:
            if item.album_id is not None:
                album = g.lib.get_album(item.album_id)
            else:
                tmp_file = tempfile.NamedTemporaryFile(prefix='beetstream-coverart-', suffix='.png')
                tmp_file_name = tmp_file.name
                try:
                    tmp_file.close()
                    subprocess.run(['ffmpeg', '-i', item.path, '-an', '-c:v',
                        'copy', tmp_file_name,
                        '-hide_banner', '-loglevel', 'error',])

                    return _send_image(tmp_file_name, size)
                finally:
                    os.remove(tmp_file_name)

    if album and album.artpath:
        image_path = album.artpath.decode('utf-8')

        if size is not None and int(size) > 0:
            return _send_image(image_path, size)

        return flask.send_file(image_path)
    else:
        return flask.abort(404)

def _send_image(path_or_bytesio, size):
    converted = BytesIO()
    img = Image.open(path_or_bytesio)

    if size is not None and int(size) > 0:
        size = int(size)
        img = img.resize((size, size))

    img.convert('RGB').save(converted, 'PNG')
    converted.seek(0)

    return flask.send_file(converted, mimetype='image/png')
