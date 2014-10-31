import os

from mock import Mock, patch, ANY
from click.testing import CliRunner

from dad.worker import proc


class TestChildProcess(object):

    @patch('dad.worker.proc.Popen')
    def test_run_dumps_spec(self, Popen):
        spec = {
            'cmd': 'ls -la',
        }
        process = proc.ChildProcess(spec)
        process.run('--foreground True --cleanup-working-dir')

        info = process.info()

        Popen.assert_called_with([
            'dad', 'run', info['spec'],
            '--working-directory', info['directory'],
            '--cleanup-working-dir',
            '--foreground'
        ])

        assert info['pid'] == Popen().pid


class TestRunner(object):

    def setup(self):
        self.here = os.path.dirname(os.path.abspath(__file__))
        self.spec = os.path.join(self.here, 'lsspec.json')
        self.cli = CliRunner()

    @patch('dad.worker.proc.daemon')
    @patch('dad.worker.proc.create_env')
    def test_only_pass_in_spec(self, create_env, daemon):
        create_env.return_value = proc.ProcessEnv(
            self.spec, self.here, 'output.log'
        )

        result = self.cli.invoke(proc.runner, [self.spec])

        assert 'Created Working Directory' in result.output
        assert 'Logging to:' in result.output

        daemon.DaemonContext.assert_called_with(
            stdout=ANY,
            stderr=ANY,
            working_directory=self.here,
        )

    @patch('dad.worker.proc.daemon')
    def test_run_in_forground(self, daemon):
        result = self.cli.invoke(proc.runner, [self.spec, '--foreground'])
        assert 'Running in the foreground' in result.output

    @patch('dad.worker.proc.daemon')
    def test_clean_up_working_dir(self, daemon):
        result = self.cli.invoke(proc.runner, [self.spec, '--cleanup-working-dir'])

        cleaned = False
        for line in result.output.split('\n'):
            if line.startswith('Cleaning up the working directory'):
                _, dirname = line.split(': ')
                assert not os.path.exists(dirname)
                cleaned = True

        assert cleaned


class TestPythonWorkerProcess(object):

    def setup(self):
        self.spec = {
            'cmd': 'ls -la',
            'python_deps': ['mock'],
        }
        self.proc = proc.PythonWorkerProcess(self.spec)

    def test_proc_setup(self):
        self.proc.install_python_deps = Mock()
        self.proc.download_files = Mock()
        self.proc.setup()
        assert self.proc.install_python_deps.called
        assert self.proc.download_files.called

    @patch('dad.worker.proc.Popen')
    def test_run_successfully(self, Popen):
        self.proc.start()

        Popen.assert_called_with(['ls', '-la'])
        assert self.proc.proc.wait.called
