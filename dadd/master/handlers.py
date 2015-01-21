import os

from flask import send_file, request, redirect, url_for, jsonify

from dadd.master import app
from dadd.master.files import FileStorage


@app.route('/')
def index():
    return redirect(url_for('admin.index'))


@app.route('/files/<path:path>', methods=['PUT', 'GET'])
def files(path):
    storage = FileStorage(app.config['STORAGE_DIR'])

    if request.method == 'PUT':
        storage.save(path, request.stream)
        resp = app.make_response('Updated %s' % path)
        resp.status_code = 202

        app.logger.info('Created: /files/%s' % path)
        return resp

    return send_file(storage.read(path))


@app.route('/files/', methods=['GET'])
def file_listing():
    if not os.path.exists(app.config['STORAGE_DIR']):
        storage = FileStorage(app.config['STORAGE_DIR'])
        storage.init()

    return jsonify({
        'files': os.listdir()
    })
