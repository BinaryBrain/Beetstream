from beetsplug.beetstream.utils import *
from beetsplug.beetstream import app
from flask import g, request, Response
import xml.etree.cElementTree as ET

@app.route('/rest/search2', methods=["GET", "POST"])
@app.route('/rest/search2.view', methods=["GET", "POST"])
def search2():
    return search(2)

@app.route('/rest/search3', methods=["GET", "POST"])
@app.route('/rest/search3.view', methods=["GET", "POST"])
def search3():
    return search(3)

def search(version):
    res_format = request.values.get('f') or 'xml'
    query = request.values.get('query') or ""
    artistCount = int(request.values.get('artistCount') or 20)
    artistOffset = int(request.values.get('artistOffset') or 0)
    albumCount = int(request.values.get('albumCount') or 20)
    albumOffset = int(request.values.get('albumOffset') or 0)
    songCount = int(request.values.get('songCount') or 20)
    songOffset = int(request.values.get('songOffset') or 0)

    songs = handleSizeAndOffset(list(g.lib.items("title:{}".format(query.replace("'", "\\'")))), songCount, songOffset)
    albums = handleSizeAndOffset(list(g.lib.albums("album:{}".format(query.replace("'", "\\'")))), albumCount, albumOffset)

    with g.lib.transaction() as tx:
        rows = tx.query("SELECT DISTINCT albumartist FROM albums")
    artists = [row[0] for row in rows]
    artists = list(filter(lambda artist: strip_accents(query).lower() in strip_accents(artist).lower(), artists))
    artists.sort(key=lambda name: strip_accents(name).upper())
    artists = handleSizeAndOffset(artists, artistCount, artistOffset)

    if (is_json(res_format)):
        return jsonpify(request, wrap_res("searchResult{}".format(version), {
            "artist": list(map(map_artist, artists)),
            "album": list(map(map_album, albums)),
            "song": list(map(map_song, songs))
        }))
    else:
        root = get_xml_root()
        search_result = ET.SubElement(root, 'searchResult{}'.format(version))

        for artist in artists:
            a = ET.SubElement(search_result, 'artist')
            map_artist_xml(a, artist)

        for album in albums:
            a = ET.SubElement(search_result, 'album')
            map_album_xml(a, album)

        for song in songs:
            s = ET.SubElement(search_result, 'song')
            map_song_xml(s, song)

        return Response(xml_to_string(root), mimetype='text/xml')
