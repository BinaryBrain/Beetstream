import xml.etree.cElementTree as ET
from beetsplug.beetstream.utils import *
from beetsplug.beetstream import app
from flask import g, request, Response
from .playlistprovider import PlaylistProvider

_playlist_provider = PlaylistProvider('')

# TODO link with https://beets.readthedocs.io/en/stable/plugins/playlist.html
@app.route('/rest/getPlaylists', methods=['GET', 'POST'])
@app.route('/rest/getPlaylists.view', methods=['GET', 'POST'])
def playlists():
    res_format = request.values.get('f') or 'xml'
    playlists = playlist_provider().playlists()
    if (is_json(res_format)):
        return jsonpify(request, wrap_res('playlists', {
            'playlist': [map_playlist(p) for p in playlists]
        }))
    else:
        root = get_xml_root()
        playlists_el = ET.SubElement(root, 'playlists')
        for p in playlists:
            playlist_el = ET.SubElement(playlists_el, 'playlist')
            map_playlist_xml(playlist_el, p)
        return Response(xml_to_string(root), mimetype='text/xml')

@app.route('/rest/getPlaylist', methods=['GET', 'POST'])
@app.route('/rest/getPlaylist.view', methods=['GET', 'POST'])
def playlist():
    res_format = request.values.get('f') or 'xml'
    id = request.values.get('id')
    playlist = playlist_provider().playlist(id)
    items = playlist.items()
    if (is_json(res_format)):
        p = map_playlist(playlist)
        p['entry'] = [_song(item.attrs['id']) for item in items]
        return jsonpify(request, wrap_res('playlist', p))
    else:
        root = get_xml_root()
        playlist_xml = ET.SubElement(root, 'playlist')
        map_playlist_xml(playlist_xml, playlist)
        for item in items:
            song = g.lib.get_item(item.attrs['id'])
            entry = ET.SubElement(playlist_xml, 'entry')
            map_song_xml(entry, song)
        return Response(xml_to_string(root), mimetype='text/xml')

def _song(id):
    return map_song(g.lib.get_item(int(id)))

def playlist_provider():
    _playlist_provider._dir = app.config['playlist_dir']
    return _playlist_provider
