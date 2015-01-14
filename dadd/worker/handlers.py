import json
import socket

import requests

from flask import request, jsonify

from dadd.worker import app
from dadd.worker import child_process
from dadd.worker.logging import LogWatcher


@app.route('/run/', methods=['POST'])
def run_process():
    info = child_process.start(request.json)
    app.logger.info('Starting: %s' % info)
    return jsonify(info)


@app.route('/register/', methods=['POST'])
def register_with_master():
    register(app.config.get('HOSTNAME'), app.config['PORT'])
    return jsonify({'message': 'ok'})


def register(port, hostname=None):
    sess = requests.Session()

    if 'USERNAME' in app.config and 'PASSWORD' in app.config:
        sess.auth = (app.config['USERNAME'], app.config['PASSWORD'])
    sess.headers = {'content-type': 'application/json'}

    try:
        url = app.config['MASTER_URL'] + '/api/hosts/'
        resp = sess.post(url, data=json.dumps({
            'host': hostname or socket.getfqdn(),
            'port': port
        }))
        if not resp.ok:
            app.logger.warning('Error registering with master: %s' %
                               app.config['MASTER_URL'])
    except Exception as e:
        app.logger.warning('Connection Error: %s' % e)


@app.route('/logs/<path:path>', methods=['POST'])
def tail_log(path):
    """Tell our worker about our pid to update the master and start a
    thread to watch the logs."""
    if not path.startswith('/'):
        path = '/' + path
    app.logger.info('Logging %s' % path)
    watcher = LogWatcher(path)
    watcher.start()
    return jsonify({'messsage': 'Added %s to the logs' % path})
