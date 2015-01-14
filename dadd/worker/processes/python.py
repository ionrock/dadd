import os

from subprocess import call, STDOUT

from dadd.worker.processes import WorkerProcess


class PythonWorkerProcess(WorkerProcess):

    def create_virtualenv(self):
        call(['virtualenv', 'venv'])

    def install_python_deps(self):
        self.create_virtualenv()

        # Make sure we have a list
        if isinstance(self.spec['python_deps'], basestring):
            self.spec['python_deps'] = [self.spec['python_deps']]

        for dep in self.spec['python_deps']:
            cmd = [
                'venv/bin/pip', 'install',
            ]

            if self.spec.get('python_cheeseshop'):
                cmd.extend(['-i', self.spec['python_cheeseshop']])

            cmd.append(dep)
            self.log('Running: %s' % ' '.join(cmd))
            call(cmd, stderr=STDOUT, stdout=self.output)

    def setup(self):
        if 'python_deps' in self.spec:
            self.install_python_deps()
        self.download_files()

    def start(self):
        # Add our virtualenv to the path
        os.environ['PATH'] += ':%s' % os.path.abspath('./venv/bin/')
        super(PythonWorkerProcess, self).start()
