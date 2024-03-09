from beetsplug.beetstream.utils import *
from beetsplug.beetstream import app
from flask import request, Response
import xml.etree.cElementTree as ET

# Fake endpoint to avoid some apps errors
@app.route('/rest/scrobble', methods=["GET", "POST"])
@app.route('/rest/scrobble.view', methods=["GET", "POST"])
@app.route('/rest/ping', methods=["GET", "POST"])
@app.route('/rest/ping.view', methods=["GET", "POST"])
def ping():
    res_format = request.values.get('f') or 'xml'

    if (is_json(res_format)):
        return jsonpify(request, {
            "subsonic-response": {
                "status": "ok",
                "version": "1.16.1"
            }
        })
    else:
        root = get_xml_root()
        return Response(xml_to_string(root), mimetype='text/xml')

@app.route('/rest/getLicense', methods=["GET", "POST"])
@app.route('/rest/getLicense.view', methods=["GET", "POST"])
def getLicense():
    res_format = request.values.get('f') or 'xml'

    if (is_json(res_format)):
        return jsonpify(request, wrap_res("license", {
            "valid": True,
            "email": "foo@example.com",
            "trialExpires": "3000-01-01T00:00:00.000Z"
        }))
    else:
        root = get_xml_root()
        l = ET.SubElement(root, 'license')
        l.set("valid", "true")
        l.set("email", "foo@example.com")
        l.set("trialExpires", "3000-01-01T00:00:00.000Z")
        return Response(xml_to_string(root), mimetype='text/xml')

@app.route('/rest/getMusicFolders', methods=["GET", "POST"])
@app.route('/rest/getMusicFolders.view', methods=["GET", "POST"])
def music_folder():
    res_format = request.values.get('f') or 'xml'
    if (is_json(res_format)):
        return jsonpify(request, wrap_res("musicFolders", {
            "musicFolder": [{
                "id": 0,
                "name": "Music"
            }]
        }))
    else:
        root = get_xml_root()
        folder = ET.SubElement(root, 'musicFolders')
        folder.set("id", "0")
        folder.set("name", "Music")

        return Response(xml_to_string(root), mimetype='text/xml')
