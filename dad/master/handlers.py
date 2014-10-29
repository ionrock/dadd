from flask import send_file, request, redirect, url_for

from dad.master import app
from dad.master.files import FileStorage


@app.route('/')
def index():
    return redirect(url_for('static', filename='index.html'))


@app.route('/files/<path>', methods=['PUT', 'GET'])
def files(path):
    storage = FileStorage(app.config['STORAGE_DIR'])

    if request.method == 'PUT':
        storage.save(path, request.stream)
        resp = app.make_response('Updated %s' % path)
        resp.status_code = 202
        return resp

    return send_file(storage.read(path))