from beetsplug.beetstream.utils import *
from beetsplug.beetstream import app
from flask import g, request, Response
from beets.random import random_objs
import xml.etree.cElementTree as ET

@app.route('/rest/getSong', methods=["GET", "POST"])
@app.route('/rest/getSong.view', methods=["GET", "POST"])
def song():
    res_format = request.values.get('f') or 'xml'
    id = int(song_subid_to_beetid(request.values.get('id')))
    song = g.lib.get_item(id)

    if (is_json(res_format)):
        return jsonpify(request, wrap_res("song", map_song(song)))
    else:
        root = get_xml_root()
        s = ET.SubElement(root, 'song')
        map_song_xml(s, song)

        return Response(xml_to_string(root), mimetype='text/xml')

@app.route('/rest/getSongsByGenre', methods=["GET", "POST"])
@app.route('/rest/getSongsByGenre.view', methods=["GET", "POST"])
def songs_by_genre():
    res_format = request.values.get('f') or 'xml'
    genre = request.values.get('genre')
    count = int(request.values.get('count') or 10)
    offset = int(request.values.get('offset') or 0)

    songs = handleSizeAndOffset(list(g.lib.items('genre:' + genre.replace("'", "\\'"))), count, offset)

    if (is_json(res_format)):
        return jsonpify(request, wrap_res("songsByGenre", {
            "song": list(map(map_song, songs))
        }))
    else:
        root = get_xml_root()
        songs_by_genre = ET.SubElement(root, 'songsByGenre')

        for song in songs:
            s = ET.SubElement(songs_by_genre, 'song')
            map_song_xml(s, song)

        return Response(xml_to_string(root), mimetype='text/xml')

@app.route('/rest/stream', methods=["GET", "POST"])
@app.route('/rest/stream.view', methods=["GET", "POST"])
def stream_song():
    maxBitrate = int(request.values.get('maxBitRate') or 0) # TODO
    format = request.values.get('format') #TODO
    return stream(maxBitrate)

@app.route('/rest/download', methods=["GET", "POST"])
@app.route('/rest/download.view', methods=["GET", "POST"])
def download_song():
    return stream(0)

def stream(maxBitrate):
    id = int(song_subid_to_beetid(request.values.get('id')))
    item = g.lib.get_item(id)

    def generate():
        with open(item.path, "rb") as songFile:
            data = songFile.read(1024)
            while data:
                yield data
                data = songFile.read(1024)
    return Response(generate(), mimetype=path_to_content_type(item.path.decode('utf-8')))

@app.route('/rest/getRandomSongs', methods=["GET", "POST"])
@app.route('/rest/getRandomSongs.view', methods=["GET", "POST"])
def random_songs():
    res_format = request.values.get('f') or 'xml'
    size = int(request.values.get('size') or 10)
    songs = list(g.lib.items())
    songs = random_objs(songs, -1, size)

    if (is_json(res_format)):
        return jsonpify(request, wrap_res("randomSongs", {
            "song": list(map(map_song, songs))
        }))
    else:
        root = get_xml_root()
        album = ET.SubElement(root, 'randomSongs')

        for song in songs:
            s = ET.SubElement(album, 'song')
            map_song_xml(s, song)

        return Response(xml_to_string(root), mimetype='text/xml')

# TODO link with Last.fm or ListenBrainz
@app.route('/rest/getTopSongs', methods=["GET", "POST"])
@app.route('/rest/getTopSongs.view', methods=["GET", "POST"])
def top_songs():
    res_format = request.values.get('f') or 'xml'
    if (is_json(res_format)):
        return jsonpify(request, wrap_res("topSongs", {}))
    else:
        root = get_xml_root()
        ET.SubElement(root, 'topSongs')
        return Response(xml_to_string(root), mimetype='text/xml')


@app.route('/rest/getStarred', methods=["GET", "POST"])
@app.route('/rest/getStarred.view', methods=["GET", "POST"])
def starred_songs():
    res_format = request.values.get('f') or 'xml'
    if (is_json(res_format)):
        return jsonpify(request, wrap_res("starred", {
            "song": []
        }))
    else:
        root = get_xml_root()
        ET.SubElement(root, 'starred')
        return Response(xml_to_string(root), mimetype='text/xml')

@app.route('/rest/getStarred2', methods=["GET", "POST"])
@app.route('/rest/getStarred2.view', methods=["GET", "POST"])
def starred2_songs():
    res_format = request.values.get('f') or 'xml'
    if (is_json(res_format)):
        return jsonpify(request, wrap_res("starred2", {
            "song": []
        }))
    else:
        root = get_xml_root()
        ET.SubElement(root, 'starred2')
        return Response(xml_to_string(root), mimetype='text/xml')
