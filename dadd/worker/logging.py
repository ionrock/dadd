import os
import threading


class LogWatcher(threading.Thread):

    def __init__(self, fname):
        super(LogWatcher, self).__init__()
        self.fname = fname

    def run(self):
        if os.path.exists(self.fname):
            for line in open(self.fname):
                print(line)
        else:
            print('%s does not exist' % self.fname)
