import time
from beetsplug.beetstream.utils import *
from beetsplug.beetstream import app
from flask import g, request, Response
import xml.etree.cElementTree as ET

@app.route('/rest/getArtists', methods=["GET", "POST"])
@app.route('/rest/getArtists.view', methods=["GET", "POST"])
def all_artists():
    return get_artists("artists")

@app.route('/rest/getIndexes', methods=["GET", "POST"])
@app.route('/rest/getIndexes.view', methods=["GET", "POST"])
def indexes():
    return get_artists("indexes")

def get_artists(version):
    res_format = request.values.get('f') or 'xml'
    with g.lib.transaction() as tx:
        rows = tx.query("SELECT DISTINCT albumartist FROM albums")
    all_artists = [row[0] for row in rows]
    all_artists.sort(key=lambda name: strip_accents(name).upper())
    all_artists = filter(lambda name: len(name) > 0, all_artists)

    indicies_dict = {}

    for name in all_artists:
        index = strip_accents(name[0]).upper()
        if index not in indicies_dict:
            indicies_dict[index] = []
        indicies_dict[index].append(name)

    if (is_json(res_format)):
        indicies = []
        for index, artist_names in indicies_dict.items():
            indicies.append({
                "name": index,
                "artist": list(map(map_artist, artist_names))
            })

        return jsonpify(request, wrap_res(version, {
            "ignoredArticles": "",
            "lastModified": int(time.time() * 1000),
            "index": indicies
        }))
    else:
        root = get_xml_root()
        indexes_xml = ET.SubElement(root, version)
        indexes_xml.set('ignoredArticles', "")

        indicies = []
        for index, artist_names in indicies_dict.items():
            indicies.append({
                "name": index,
                "artist": artist_names
            })

        for index in indicies:
            index_xml = ET.SubElement(indexes_xml, 'index')
            index_xml.set('name', index["name"])

            for a in index["artist"]:
                artist = ET.SubElement(index_xml, 'artist')
                map_artist_xml(artist, a)

        return Response(xml_to_string(root), mimetype='text/xml')

@app.route('/rest/getArtist', methods=["GET", "POST"])
@app.route('/rest/getArtist.view', methods=["GET", "POST"])
def artist():
    res_format = request.values.get('f') or 'xml'
    artist_id = request.values.get('id')
    artist_name = artist_id_to_name(artist_id)
    albums = g.lib.albums(artist_name.replace("'", "\\'"))
    albums = filter(lambda album: album.albumartist == artist_name, albums)

    if (is_json(res_format)):
        return jsonpify(request, wrap_res("artist", {
            "id": artist_id,
            "name": artist_name,
            "album": list(map(map_album, albums))
        }))
    else:
        root = get_xml_root()
        artist_xml = ET.SubElement(root, 'artist')
        artist_xml.set("id", artist_id)
        artist_xml.set("name", artist_name)

        for album in albums:
            a = ET.SubElement(artist_xml, 'album')
            map_album_xml(a, album)

        return Response(xml_to_string(root), mimetype='text/xml')

@app.route('/rest/getArtistInfo2', methods=["GET", "POST"])
@app.route('/rest/getArtistInfo2.view', methods=["GET", "POST"])
def artistInfo2():
    res_format = request.values.get('f') or 'xml'
    artist_name = artist_id_to_name(request.values.get('id'))

    if (is_json(res_format)):
        return jsonpify(request, wrap_res("artistInfo2", {
            "biography": f"wow. much artist. very {artist_name}",
            "musicBrainzId": "",
            "lastFmUrl": "",
            "smallImageUrl": "",
            "mediumImageUrl": "",
            "largeImageUrl": ""
        }))
    else:
        root = get_xml_root()
        artist_xml = ET.SubElement(root, 'artistInfo2')

        biography = ET.SubElement(artist_xml, "biography")
        biography.text = f"wow. much artist very {artist_name}."
        musicBrainzId = ET.SubElement(artist_xml, "musicBrainzId")
        musicBrainzId.text = ""
        lastFmUrl = ET.SubElement(artist_xml, "lastFmUrl")
        lastFmUrl.text = ""
        smallImageUrl = ET.SubElement(artist_xml, "smallImageUrl")
        smallImageUrl.text = ""
        mediumImageUrl = ET.SubElement(artist_xml, "mediumImageUrl")
        mediumImageUrl.text = ""
        largeImageUrl = ET.SubElement(artist_xml, "largeImageUrl")
        largeImageUrl.text = ""

        return Response(xml_to_string(root), mimetype='text/xml')
