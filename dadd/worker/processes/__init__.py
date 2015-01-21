import os
import shlex

from subprocess import call, STDOUT

from dadd.worker import app
from dadd.worker.utils import printf
from dadd import client


class WorkerProcess(object):

    def __init__(self, spec, output, sess=None):
        self.spec = spec
        # TODO: Add auth from the global config
        self.conn = client.connect(app, sess)
        self.output = output
        self.returncode = None

    def setup(self):
        self.download_files()

    def log(self, msg):
        printf(msg, self.output)
        app.logger.info(msg)

    def start(self):
        if isinstance(self.spec['cmd'], basestring):
            parts = shlex.split(self.spec['cmd'])
        else:
            parts = self.spec['cmd']

        cmd = []
        for part in parts:
            if part == '$APP_SETTINGS':
                part = os.environ['APP_SETTINGS_JSON']
            cmd.append(part)

        self.log('Running: %s' % ' '.join(cmd))

        self.returncode = call(cmd, stdout=self.output, stderr=STDOUT)

    def download_files(self):
        for filename, url in self.spec.get('download_urls', {}).iteritems():
            resp = self.conn.sess.get(url, stream=True)
            resp.raise_for_status()

            with open(filename, 'w+') as fh:
                for chunk in resp:
                    fh.write(chunk)

            self.log('Downloaded: %s to %s' % (url, filename))

    def finish(self):
        state = 'success'
        if self.returncode:
            state = 'failed'
        client.set_process_state(self.conn, self.proc.pid, state)

    @property
    def code(self):
        return self.proc.returncode
