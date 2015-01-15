import os
import time
import threading

from dadd.worker import app


class LogWatcher(threading.Thread):

    def __init__(self, fname, pid, timeout=10):
        super(LogWatcher, self).__init__()
        self.fname = fname
        self.pid = pid
        self.timeout = timeout

    def write(self, chunk):
        app.logger.info(chunk)

    def running(self):
        try:
            os.kill(self.pid, 0)
            # The process is running
            return True
        except OSError as e:
            app.logger.info(e)
            app.logger.info('%s is down' % self.pid)
            return False

        return os.path.exists(self.fname)

    def run(self):
        self.write('Tailing: %s' % self.fname)
        if not os.path.exists(self.fname):
            return

        with open(self.fname) as fh:
            while self.running():
                line = fh.readline()
                if not line:
                    time.sleep(1)
                    print('sleeping')
                else:
                    self.write(line)

        self.write('Done tailing %s' % self.fname)
