import glob
import os
import pathlib
import re
import sys
from flask import current_app as app
from werkzeug.utils import safe_join

extinf_regex = re.compile(r'^#EXTINF:([0-9]+)( [^,]+)?,[\s]*(.*)')
highint32 = 1<<31

class PlaylistProvider:
    def __init__(self, dir):
        self.dir = dir
        self._playlists = {}

    def _refresh(self):
        self._playlists = {p.id: p for p in self._load_playlists()}
        app.logger.debug(f"Loaded {len(self._playlists)} playlists")

    def _load_playlists(self):
        paths = glob.glob(os.path.join(self.dir, "**.m3u8"))
        paths += glob.glob(os.path.join(self.dir, "**.m3u"))
        paths.sort()
        for path in paths:
            try:
                yield self._playlist(path)
            except Exception as e:
                app.logger.error(f"Failed to load playlist {filepath}: {e}")

    def playlists(self):
        self._refresh()
        playlists = self._playlists
        ids = [k for k, v in playlists.items() if v]
        ids.sort()
        return [playlists[id] for id in ids]

    def playlist(self, id):
        filepath = safe_join(self.dir, id)
        playlist = self._playlist(filepath)
        if playlist.id not in self._playlists: #  add to cache
            playlists = self._playlists.copy()
            playlists[playlist.id] = playlist
            self._playlists = playlists
        return playlist

    def _playlist(self, filepath):
        id = self._path2id(filepath)
        name = pathlib.Path(os.path.basename(filepath)).stem
        playlist = self._playlists.get(id)
        mtime = pathlib.Path(filepath).stat().st_mtime
        if playlist and playlist.modified == mtime:
            return playlist # cached metadata
        app.logger.debug(f"Loading playlist {filepath}")
        return Playlist(id, name, mtime, filepath)

    def _path2id(self, filepath):
        return os.path.relpath(filepath, self.dir)

class Playlist:
    def __init__(self, id, name, modified, path):
        self.id = id
        self.name = name
        self.modified = modified
        self.path = path
        self.count = 0
        self.duration = 0
        artists = {}
        max_artists = 10
        for item in self.items():
            self.count += 1
            self.duration += item.duration
            artist = Artist(item.title.split(' - ')[0])
            found = artists.get(artist.key)
            if found:
                found.count += 1
            else:
                if len(artists) > max_artists:
                    l = _sortedartists(artists)[:max_artists]
                    artists = {a.key: a for a in l}
                artists[artist.key] = artist
        self.artists = ', '.join([a.name for a in _sortedartists(artists)])

    def items(self):
        return parse_m3u_playlist(self.path)

def _sortedartists(artists):
    l = [a for _,a in artists.items()]
    l.sort(key=lambda a: (highint32-a.count, a.name))
    return l

class Artist:
    def __init__(self, name):
        self.key = name.lower()
        self.name = name
        self.count = 1

def parse_m3u_playlist(filepath):
    '''
    Parses an M3U playlist and yields its items, one at a time.
    CAUTION: Attribute values that contain ',' or ' ' are not supported!
    '''
    with open(filepath, 'r', encoding='UTF-8') as file:
        linenum = 0
        item = PlaylistItem()
        while line := file.readline():
            line = line.rstrip()
            linenum += 1
            if linenum == 1:
                assert line == '#EXTM3U', f"File {filepath} is not an EXTM3U playlist!"
                continue
            if len(line.strip()) == 0:
                continue
            m = extinf_regex.match(line)
            if m:
                item = PlaylistItem()
                duration = m.group(1)
                item.duration = int(duration)
                attrs = m.group(2)
                if attrs:
                    item.attrs = {k: v.strip('"') for k,v in [kv.split('=') for kv in attrs.strip().split(' ')]}
                else:
                    item.attrs = {}
                item.title = m.group(3)
                continue
            if line.startswith('#'):
                continue
            item.uri = line
            yield item
            item = PlaylistItem()

class PlaylistItem():
    def __init__(self):
        self.title = None
        self.duration = None
        self.uri = None
        self.attrs = None
