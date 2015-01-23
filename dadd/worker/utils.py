import json
import subprocess

import requests


def get_hostname(app):
    hostname = subprocess.check_output(['hostname', '-f']).strip()
    app.logger.info('hostname: %s' % hostname)
    return hostname


def register(app, port, hostname=None):
    hostname = hostname or get_hostname(app)

    sess = requests.Session()

    if 'USERNAME' in app.config and 'PASSWORD' in app.config:
        sess.auth = (app.config['USERNAME'], app.config['PASSWORD'])
    sess.headers = {'content-type': 'application/json'}

    try:
        url = app.config['MASTER_URL'] + '/api/hosts/'
        resp = sess.post(url, data=json.dumps({
            'host': hostname,
            'port': port
        }))
        if not resp.ok:
            app.logger.warning('Error registering with master: %s' %
                               app.config['MASTER_URL'])
    except Exception as e:
        app.logger.warning('Connection Error: %s' % e)


def printf(msg, fh):
    "Print to a file handle."
    fh.write(msg + '\n')
    fh.flush()


def call_cmd(cmd, output):
    "Call a command sending stdout/stderr to an output file handle."
    if isinstance(cmd, basestring):
        cmd = cmd.split()

    printf('Running Cmd: %s\n' % cmd, output)

    return subprocess.call(cmd,
                           stdout=output,
                           stderr=subprocess.STDOUT)
