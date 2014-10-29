import requests

from dad.master.models import db, Host


def get_session():
    sess = requests.Session()
    # Unused currently
    # sess.auth = (app.config['USERNAME'], app.config['PASSWORD'])
    sess.headers = {'content-type': 'application/json'}
    return sess


def find_host():
    procs = 0
    current_host = None
    for host in db.session.query(Host).all():
        if not current_host:
            current_host = host

        num_procs = len(host.procs)

        # If we have a host without any proces we'll use that right
        # off the back.
        if num_procs == 0:
            break

        if num_procs >= procs:
            current_host = host

    if not current_host:
        raise Exception('No workers available!')

    # See if the host is up and running. If not let's delete it.
    try:
        requests.get('http://%s/' % str(current_host))
        return current_host
    except requests.exceptions.ConnectionError:
        db.session.delete(host)
        return find_host()
