from beetsplug.beetstream.utils import *
from beetsplug.beetstream import app
from flask import g, request, Response
import xml.etree.cElementTree as ET

@app.route('/rest/getUser', methods=["GET", "POST"])
@app.route('/rest/getUser.view', methods=["GET", "POST"])
def user():
    res_format = request.values.get('f') or 'xml'
    if (is_json(res_format)):
        return jsonpify(request, wrap_res("user", {
            "username" : "admin",
            "email" : "foo@example.com",
            "scrobblingEnabled" : True,
            "adminRole" : True,
            "settingsRole" : True,
            "downloadRole" : True,
            "uploadRole" : True,
            "playlistRole" : True,
            "coverArtRole" : True,
            "commentRole" : True,
            "podcastRole" : True,
            "streamRole" : True,
            "jukeboxRole" : True,
            "shareRole" : True,
            "videoConversionRole" : True,
            "avatarLastChanged" : "1970-01-01T00:00:00.000Z",
            "folder" : [ 0 ]
        }))
    else:
        root = get_xml_root()
        u = ET.SubElement(root, 'user')
        u.set("username", "admin")
        u.set("email", "foo@example.com")
        u.set("scrobblingEnabled", "true")
        u.set("adminRole", "true")
        u.set("settingsRole", "true")
        u.set("downloadRole", "true")
        u.set("uploadRole", "true")
        u.set("playlistRole", "true")
        u.set("coverArtRole", "true")
        u.set("commentRole", "true")
        u.set("podcastRole", "true")
        u.set("streamRole", "true")
        u.set("jukeboxRole", "true")
        u.set("shareRole", "true")
        u.set("videoConversionRole", "true")
        u.set("avatarLastChanged", "1970-01-01T00:00:00.000Z")
        f = ET.SubElement(u, 'folder')
        f.text = "0"

        return Response(xml_to_string(root), mimetype='text/xml')
