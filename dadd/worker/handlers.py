import os

from flask import request, jsonify

from dadd.worker import app
from dadd.worker import child_process
from dadd.worker.logging import LogWatcher
from dadd.worker.utils import get_hostname, register


@app.route('/run/', methods=['POST'])
def run_process():
    foreground = app.config.get('RUNNER_FOREGROUND', False)
    info = child_process.start(request.json, foreground)

    app.logger.info('Starting: %s' % info)

    if not foreground:
        watcher = LogWatcher(
            os.path.join(info['directory'], 'output.log'),
            info['pid']
        )
        watcher.start()
    return jsonify(info)


@app.route('/register/', methods=['POST'])
def register_with_master():
    hostname = get_hostname(app)
    register(app.config['PORT'], hostname=hostname)
    return jsonify({'message': 'ok'})


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
