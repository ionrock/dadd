import os

import requests
import yaml


def get_session():
    sess = requests.Session()
    # Unused currently
    # sess.auth = (app.config['USERNAME'], app.config['PASSWORD'])
    sess.headers = {'content-type': 'application/json'}
    return sess


def update_config(app):
    if 'HOST' in os.environ:
        app.config['HOST'] = os.environ['HOST']

    if 'PORT' in os.environ:
        app.config['PORT'] = os.environ['PORT']

    if 'DEBUG' in os.environ:
        app.debug = True

    if os.environ.get('APP_SETTINGS_YAML'):
        config = yaml.safe_load(open(os.environ['APP_SETTINGS_YAML']))
        app.config.update(config)
