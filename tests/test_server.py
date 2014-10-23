import os
import time

import pytest
import requests
import json
import yaml


HERE = os.path.dirname(os.path.abspath(__file__))


@pytest.fixture()
def sess():
    sess = requests.Session()
    sess.headers = {
        'Content-Type': 'application/json'
    }
    return sess


class TestStartProc(object):

    def test_start_proc(self, sess):
        doc = {
            'cmd': 'python -m SimpleHTTPServer 7000'.split()
        }

        resp = sess.post('http://localhost:5000/run/',
                         data=json.dumps(doc))
        result = resp.json()
        assert os.path.exists('/proc/%s' % result['pid'])
        assert os.kill(result['pid'], 0) is None


class TestStartHelloProc(object):
    url = 'http://localhost:5000/files/hello_server.py'
    example_server = os.path.join(HERE, '..', 'example', 'hello_server.py')
    example_spec = os.path.join(HERE, '..', 'example', 'hello_spec.yaml')

    def put_file(self, sess):
        resp = sess.put(self.url,
                        headers={'Content-Type': 'application/octet-stream'},
                        data=open(self.example_server))
        assert resp.ok

    def start_process(self, sess):
        spec = yaml.safe_load(open(self.example_spec))
        resp = sess.post('http://localhost:5000/api/procs/',
                         data=json.dumps(spec))
        assert resp.ok

    def test_put_file(self, sess):
        self.put_file(sess)

        resp = sess.get(self.url)
        assert resp.ok
        assert resp.content == open(self.hello_server).read()

    def test_run_hello_server(self, sess):
        self.put_file(sess)
        self.start_process(sess)

        time.sleep(10)

        resp = sess.get('http://localhost:6010/')
        assert resp.ok
        assert resp.content == 'Hello World!'
