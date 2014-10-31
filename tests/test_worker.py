import os
import json

from dad.worker import app


class TestStartProc(object):

    def setup(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

    def test_start_proc(self):
        doc = {
            'cmd': 'python -m SimpleHTTPServer 7000'.split()
        }

        resp = self.app.post('/run/', data=json.dumps(doc))
        result = json.loads(resp.data)
        assert os.path.exists('/proc/%s' % result['pid'])
        assert os.kill(result['pid'], 0) is None
