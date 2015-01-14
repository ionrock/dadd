import os
import json
import shutil

from contextlib import contextmanager

import click
import daemon

from erroremail import ErrorEmail

from dadd import client
from dadd.worker import app
from dadd.worker.child_process import create_env, ProcessEnv
from dadd.worker.processes.python import PythonWorkerProcess
from dadd.master.utils import update_config
from dadd.runner.logger import get_logger


def printf(msg, fh):
    fh.write(msg + '\n')
    fh.flush()


@contextmanager
def foreground_context():
    yield


class ErrorHandler(object):
    def __init__(self, spec, logfile, sess=None):
        self.spec = spec
        self.logfile = logfile
        self.conn = client.connect(app, sess)
        self.log = get_logger(logfile)

    def upload_log(self):
        if not os.path.exists(self.logfile):
            return

        with open(self.logfile, 'r') as logfile:
            pid = client.get_pid(self.spec)
            if pid:
                client.set_proc_logfile(self.conn, pid, logfile)
            else:
                self.log.info('No process_id in spec. Here is the log.')
                for line in logfile:
                    self.log.info(line)

    def send_error_email(self, *args):
        if 'ERROR_EMAIL_CONFIG' in app.config:
            mailer = ErrorEmail(app.config['ERROR_EMAIL_CONFIG'])
            message = mailer.create_message_from_traceback(args)
            mailer.send_email(message)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pid = client.get_pid(self.spec)

        if None in args:
            # client.set_process_state(self.conn, pid, 'success')
            return True

        self.upload_log()
        client.set_process_state(self.conn, pid, 'failed')
        self.send_error_email(*args)
        return True


def find_env(spec, working_dir):
    # Create a directory to work under and specify our log file.
    if working_dir:
        env = ProcessEnv(
            spec, working_dir,
            os.path.join(os.path.abspath(working_dir), 'output.log')
        )
        return env

    env = create_env(spec)
    print('Created Working Directory: %s' % env.directory)
    return env


def configure_environ(spec):
    # Add our spec as an APP_SETTINGS_JSON now that we are daemonized.
    config_filename = os.path.abspath('./specfile.json')
    with open(config_filename, 'w+') as fh:
        json.dump(spec, fh)
    os.environ['APP_SETTINGS_JSON'] = config_filename


def run_in_foreground(foreground):
    if app.config.get('RUNNER_FOREGROUND'):
        return True
    return foreground


@click.command()
@click.argument('specfile', type=click.File())
@click.option('--no-cleanup', is_flag=True)
@click.option('--foreground', is_flag=True)
@click.option('--working-dir', '-w')
def runner(specfile, no_cleanup, foreground, working_dir=None):
    # Make sure our config is up to date with our parent
    update_config(app)
    app.logger.info('update config before daemonizing')

    # Load our spec file
    spec = json.load(specfile)
    app.logger.info('loading the spec file')

    env = find_env(spec, working_dir)

    run_context = daemon.DaemonContext(
        detach_process=run_in_foreground(foreground),
        working_directory=working_dir
    )

    # TODO: Make sure we give our worker a chance to do clean up
    #       and notify the master on any errors.
    # run_context.signal_map.update({
    #     signal.SIGTERM: worker.cleanup,
    # })

    with run_context:

        with ErrorHandler(spec, env.logfile) as error_handler:
            configure_environ(spec)

            with open(env.logfile, 'w+') as output:
                worker = PythonWorkerProcess(spec, output)

                printf('Setting up', output)
                worker.setup()
                printf('Starting', output)
                try:
                    worker.start()
                except:
                    import traceback
                    printf(traceback.format_exc())
                    error_handler.upload_log()
                    raise

                printf('Finishing', output)
                worker.finish()
                printf('Done')

        # NOTE: These log messages essentiall fall into the ether b/c
        #       we are daemonized had to close our log file before
        #       uploading it...
        if no_cleanup:
            app.logger.info('Not cleaning up %s' % working_dir)
        else:
            app.logger.info('Cleaning up the working directory: %s' % working_dir)
            shutil.rmtree(working_dir)
