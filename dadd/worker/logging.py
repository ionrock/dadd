import os
import time
import threading

from dadd.worker import app


class LogWatcher(threading.Thread):

    def __init__(self, fname):
        super(LogWatcher, self).__init__()
        self.fname = fname

    def write(self, chunk):
        app.logger.info(chunk)

    def running(self):
        try:
            os.kill(self.pid, 0)
            app.logger.info('%s is up' % self.pid)
            return True
        except OSError:
            app.logger.info('%s is down' % self.pid)
            return False

    def tail(self, fh):
        self.write('Tailing: %s' % fh.name)
        curr_position = fh.tell()
        line = fh.readline()
        if not line:
            fh.seek(curr_position)
        else:
            self.write(line)

    def run(self):
        if os.path.exists(self.fname):
            return self.tail(open(self.fname))
