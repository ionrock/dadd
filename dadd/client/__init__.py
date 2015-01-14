import os
import requests

from pprint import pprint
from collections import namedtuple

Connection = namedtuple('DaddConnection', [
    'sess', 'config', 'base'
])


def connect(app, session=None):
    sess = session or requests.Session()
    base = os.environ.get('MASTER_URL', app.config['MASTER_URL'])
    return Connection(sess, app.config, base)


def get_pid(spec):
    return spec.get('process_id')


def procs_url(base, pid, tail):
    return '%s/api/procs/%s/%s' % (base, pid, tail)


def set_proc_logfile(conn, pid, logfile):
    url = procs_url(conn.base, pid, 'logfile/')
    headers = {'content-type': 'text/plain'}
    conn.sess.post(url, headers=headers, data=logfile)


def set_process_state(conn, pid, state):
    resp = conn.sess.post(procs_url(conn.base, pid, '%s/' % state))
    if not resp.ok:
        print(resp.request.url)
        pprint(dict(resp.headers))
        print(resp.content)
        resp.raise_for_status()
