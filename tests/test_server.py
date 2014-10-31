import os
import time

import pytest
import requests
import json
import yaml

from pprint import pprint


HERE = os.path.dirname(os.path.abspath(__file__))


@pytest.fixture()
def sess():
    sess = requests.Session()
    sess.headers = {
        'Content-Type': 'application/json'
    }
    return sess


class TestStartProc(object):

    def test_start_proc(self, sess, servers):
        doc = {
            'cmd': 'python -m SimpleHTTPServer 7000'.split()
        }

        print(servers.worker + '/run/')
        resp = sess.post(servers.worker + '/run/',
                         data=json.dumps(doc))
        result = resp.json()
        assert os.path.exists('/proc/%s' % result['pid'])
        assert os.kill(result['pid'], 0) is None


class TestStartHelloProc(object):
    example_server = os.path.join(HERE, '..', 'example', 'hello_server.py')
    example_spec = os.path.join(HERE, '..', 'example', 'hello_spec.yaml')

    def put_file(self, sess, url):
        resp = sess.put(url + '/files/hello_server.py',
                        headers={'Content-Type': 'application/octet-stream'},
                        data=open(self.example_server))
        assert resp.ok

    def start_process(self, sess, url):
        spec = yaml.safe_load(open(self.example_spec))
        resp = sess.post(url,
                         data=json.dumps(spec))
        if not resp.ok:
            pprint(dict(resp.headers))
            print(resp.content)
        assert resp.ok

    def test_put_file(self, sess, servers):
        self.put_file(sess, servers.master)

        resp = sess.get(servers.master + '/files/hello_server.py')
        assert resp.ok
        assert resp.content == open(self.example_server).read()

    def test_run_hello_server(self, sess, servers):
        self.put_file(sess, servers.master)
        self.start_process(sess, servers.master + '/api/procs/')

        resp = sess.get('http://localhost:7000/')
        assert resp.ok
        assert resp.content == 'Hello World!'
