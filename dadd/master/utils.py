import requests


def get_session():
    sess = requests.Session()
    # Unused currently
    # sess.auth = (app.config['USERNAME'], app.config['PASSWORD'])
    sess.headers = {'content-type': 'application/json'}
    return sess
