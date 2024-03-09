import glob
import os
import pathlib
import re
from werkzeug.utils import safe_join

extinf_regex = re.compile(r'^#EXTINF:([0-9]+)( [^,]+)?,[\s]*(.*)')

class PlaylistProvider:
    def __init__(self, dir):
        self._dir = dir
        self._playlists = {}

    def _refresh(self):
        paths = glob.glob(os.path.join(self._dir, "**.m3u8"))
        paths += glob.glob(os.path.join(self._dir, "**.m3u"))
        paths.sort()
        self._playlists = {self._path2id(p): self._playlist(p) for p in paths}

    def playlists(self):
        self._refresh()
        ids = [k for k in self._playlists]
        ids.sort()
        return [self._playlists[id] for id in ids]

    def playlist(self, id):
        self._refresh()
        filepath = safe_join(self._dir, id)
        return self._playlist(filepath)

    def _playlist(self, filepath):
        id = self._path2id(filepath)
        name = pathlib.Path(os.path.basename(filepath)).stem
        playlist = self._playlists.get(id)
        mtime = pathlib.Path(filepath).stat().st_mtime
        if playlist and playlist.modified == mtime:
            return playlist # cached
        return Playlist(id, name, mtime, filepath)

    def _path2id(self, filepath):
        return os.path.relpath(filepath, self._dir)

class Playlist():
    def __init__(self, id, name, modified, path):
        self.id = id
        self.name = name
        self.modified = modified
        self.path = path
        self.count = 0
        self.duration = 0
        for item in parse_m3u_playlist(self.path):
            self.count += 1
            self.duration += item.duration

    def items(self):
        return parse_m3u_playlist(self.path)

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
