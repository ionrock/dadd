import os
import json
import random

import yaml

from dadd.master import app
from dadd.master.models import Process, Host, db

HERE = os.path.dirname(os.path.abspath(__file__))


class TestMasterHostAPI(object):

    def setup(self):
        app.config['TESTING'] = True
        hosts = db.session.query(Host).all()
        for host in hosts:
            db.session.delete(host)
        db.session.commit()
        self.app = app.test_client()

    def create_host(self):
        doc = {
            'host': 'myhost',
            'port': '9001'
        }
        resp = self.app.post('/api/hosts/',
                             headers={'content-type': 'application/json'},
                             data=json.dumps(doc))
        return json.loads(resp.data)

    def test_host_registration(self):
        doc = self.create_host()
        assert 'created' in doc
        resp = self.app.get(doc['created'])
        assert resp.status_code == 200
        assert json.loads(resp.data)['uri']

    def test_hosts_list(self):
        self.create_host()
        resp = self.app.get('/api/hosts/')
        doc = json.loads(resp.data)
        assert 'hosts' in doc and doc['hosts']

    def test_delete_host(self):
        doc = self.create_host()
        resp = self.app.delete(doc['created'])
        doc = json.loads(resp.data)
        assert 'deleted' in doc


class TestMasterProcAPI(object):

    def setup(self):
        app.config['TESTING'] = True
        procs = db.session.query(Process).all()
        for proc in procs:
            db.session.delete(proc)
        db.session.commit()
        self.app = app.test_client()

    def add_proc(self, host=None, port=9010):
        """Add a proc in the DB"""

        host = Host(host=host or 'myhost', port=port or '9010')
        proc = Process(spec={'cmd': 'ls'},
                       host=host,
                       pid=random.randint(10, 50))

        db.session.add(host)
        db.session.add(proc)
        db.session.commit()
        return proc.id

    def test_proc_set_state(self):
        proc_id = self.add_proc()
        self.app.post('/api/procs/%s/success/' % proc_id)
        resp = self.app.get('/api/procs/%s/' % proc_id)
        print(proc_id)
        print(resp.data)
        doc = json.loads(resp.data)
        assert doc['state'] == 'success'

    def test_proc_set_logfile(self):
        proc_id = self.add_proc()
        resp = self.app.post(
            '/api/procs/%s/logfile/' % proc_id,
            headers={'content-type': 'text/plain'},
            data='\n'.join(['hello', 'world'])
        )

        assert resp.status_code == 200

        resp = self.app.get('/api/procs/%s/logfile/' % proc_id)
        assert 'hello' in resp.data
        assert 'world' in resp.data

    def test_proc_listing(self):
        # add some proces
        self.add_proc('a', '9000')
        self.add_proc('b', '9000')
        self.add_proc('c', '9000')

        resp = self.app.get('/api/procs/')
        assert resp.status_code == 200

        doc = json.loads(resp.data)
        assert len(doc['procs']) == 3
        assert 'next' in doc
        assert 'prev' in doc


class TestFileServing(object):
    example_server = os.path.join(HERE, '..', 'example', 'hello_server.py')
    example_spec = os.path.join(HERE, '..', 'example', 'hello_spec.yaml')

    def setup(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

    def put_file(self):
        resp = self.app.put(
            '/files/hello_server.py',
            headers={'Content-Type': 'application/octet-stream'},
            data=open(self.example_server).read()
        )
        assert resp.status_code == 202

    def start_process(self, url):
        spec = yaml.safe_load(open(self.example_spec))
        resp = self.app.post(
            url, data=json.dumps(spec)
        )

        assert resp.status_code == 200

    def test_put_file(self):
        self.put_file()
        resp = self.app.get('/files/hello_server.py')
        assert resp.data == open(self.example_server).read()
