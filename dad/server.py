# -*- coding: utf-8 -*-
import os

from flask import Flask, request, jsonify, send_file

from dad.proc import ChildProcess
from dad.files import FileStorage


app = Flask(__name__)


@app.route('/run/', methods=['POST'])
def run_process():
    proc = ChildProcess(request.json)
    proc.run()
    return jsonify(proc.info())


@app.route('/files/<path>', methods=['PUT', 'GET'])
def files(path):
    storage = FileStorage(app.config['storage_dir'])

    if request.method == 'PUT':
        storage.save(path, request.stream)
        resp = app.make_response('Updated %s' % path)
        resp.status_code = 202
        return resp

    return send_file(storage.read(path))


def run():
    app.config['storage_dir'] = os.path.join(os.getcwd(), 'temp_files')
    app.debug = True
    app.run()
