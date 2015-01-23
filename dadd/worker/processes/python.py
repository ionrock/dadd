import os

from dadd.worker.processes import WorkerProcess
from dadd.worker.utils import printf, call_cmd


class PythonWorkerProcess(WorkerProcess):

    def install_virtualenv(self):
        printf('Installing virtualenv package', self.output)
        call_cmd('pip install --upgrade virtualenv', self.output)

    def create_virtualenv(self, name='dadd-worker-venv'):
        self.install_virtualenv()
        printf('Creating the virtualenv', self.output)
        call_cmd(['virtualenv', name], self.output)

        venv_bin = os.path.abspath(os.path.join(name, 'bin'))
        os.environ['PATH'] = venv_bin + ':' + os.environ['PATH']
        self.log('Updated Path: %s' % os.environ['PATH'])

    def install_python_deps(self):
        self.create_virtualenv()

        # Make sure we have a list
        if isinstance(self.spec['python_deps'], basestring):
            self.spec['python_deps'] = [self.spec['python_deps']]

        for dep in self.spec['python_deps']:
            cmd = ['pip', 'install']

            if self.spec.get('python_cheeseshop'):
                cmd.extend(['-i', self.spec['python_cheeseshop']])

            cmd.append(dep)
            self.log('Running: %s' % ' '.join(cmd))
            call_cmd(cmd, self.output)

    def setup(self):
        super(PythonWorkerProcess, self).setup()
        if 'python_deps' in self.spec:
            self.install_python_deps()
