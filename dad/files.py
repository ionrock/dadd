import os


class FileStorage(object):

    def __init__(self, path):
        self.path = path

    def save(self, name, input):
        if not os.path.exists(self.path):
            os.mkdir(self.path)

        filename = os.path.join(self.path, name)
        with open(filename, 'w+') as output:
            for chunk in input:
                output.write(chunk)

    def read(self, name):
        return os.path.join(self.path, name)
