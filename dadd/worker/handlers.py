import os
import json
import socket

import requests

from flask import request, jsonify, Response, abort

from dadd.worker import app
from dadd.worker.proc import ChildProcess


@app.route('/run/', methods=['POST'])
def run_process():
    proc = ChildProcess(request.json)
    proc.run()
    return jsonify(proc.info())


@app.route('/register/', methods=['POST'])
def register_with_master():
    register(app.config['HOST'], app.config['PORT'])
    return jsonify({'message': 'ok'})


def register(host, port):
    sess = requests.Session()

    if 'USERNAME' in app.config and 'PASSWORD' in app.config:
        sess.auth = (app.config['USERNAME'], app.config['PASSWORD'])
    sess.headers = {'content-type': 'application/json'}

    try:
        url = app.config['MASTER_URL'] + '/api/hosts/'
        resp = sess.post(url, data=json.dumps({
            'host': app.config.get('HOSTNAME', socket.getfqdn()),
            'port': port
        }))
        if not resp.ok:
            app.logger.warning('Error registering with master: %s' %
                               app.config['MASTER_URL'])
    except Exception as e:
        app.logger.warning('Connection Error: %s' % e)


@app.route('/logs/<path:path>', methods=['GET'])
def tail_log(path):
    path = '/' + path
    if os.path.exists(path) and path.startswith('/tmp/'):
        return Response(open(path), content_type='text/plain')
    abort(404)
