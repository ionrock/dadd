import json

import requests

from flask import request, jsonify

from dad.worker import app
from dad.worker.proc import ChildProcess


@app.route('/run/', methods=['POST'])
def run_process():
    proc = ChildProcess(request.json)
    proc.run()
    return jsonify(proc.info())


@app.route('/register/', methods=['POST'])
def register_with_master():
    register(app)
    return jsonify({'message': 'ok'})


def register(app):
    sess = requests.Session()
    # TODO: Implement auth in master
    # sess.auth = (app.config['USERNAME'], app.config['PASSWORD'])
    sess.headers = {'content-type': 'application/json'}
    port = app.config['PORT']
    host = app.config['HOST']
    try:
        url = app.config['MASTER_URL'] + '/api/hosts/'
        resp = sess.post(url, data=json.dumps({
            'host': host, 'port': port
        }))
        if not resp.ok:
            # TODO: Use flask logging?
            print('Error registering with master: %s' % app.config['MASTER_URL'])
        print(resp.json())
    except Exception as e:
        print('Connection Error: %s' % e)
