import os


class FileStorage(object):

    def __init__(self, path):
        self.path = path

    def save(self, name, input):
        if not os.path.exists(self.path):
            os.mkdir(self.path)

        try:
            os.makedirs(os.path.join(self.path, os.path.dirname(name)))
        except (IOError, OSError):
            pass

        filename = os.path.join(self.path, name)
        with open(filename, 'w+') as output:
            for chunk in input:
                output.write(chunk)

    def read(self, name):
        return os.path.join(self.path, name)

    def listing(self):
        files = []
        for dirpath, dirnames, filenames in os.walk(self.path):
            for name in filenames:
                if not name.startswith('.') and not dirpath.startswith('.'):
                    files.append(os.path.join(dirpath, name))
        return files
