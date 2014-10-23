import json

import requests

from flask import send_file, request, jsonify

from dad.master import app
from dad.master.files import FileStorage
from dad.master.models import db, Process, Host


def get_session():
    sess = requests.Session()
    # Unused currently
    # sess.auth = (app.config['USERNAME'], app.config['PASSWORD'])
    sess.headers = {'content-type': 'application/json'}
    return sess


@app.route('/')
def index():
    return 'the homepage'


# Host Registration
@app.route('/api/hosts/', methods=['POST'])
def api_register_host():
    doc = request.json
    host = Host(host=doc['host'], port=doc['port'])
    query = db.session.query(Host).filter_by(host=host.host, port=host.port)
    if not query.count():
        db.session.add(host)
        db.session.commit()
        return jsonify({'created': str(host)})
    return jsonify({'exists': str(host)})


@app.route('/api/hosts/', methods=['GET'])
def api_view_hosts():
    hosts = Host.query.all()
    return jsonify({
        'hosts': [str(host) for host in hosts]
    })


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


    # See if the host is up and running. If not let's delete it.
    try:
        requests.get('http://%s/' % str(host))
        return current_host
    except requests.exceptions.ConnectionError:
        db.session.delete(host)
        return find_host()


# Start an app
@app.route('/api/procs/', methods=['POST'])
def api_create_proc():
    doc = request.json

    # Find a host
    host = find_host()

    # Try creating the process via the host
    url = 'http://%s/run/' % str(host)
    sess = get_session()
    print('Creating app on host: %s' % url)
    resp = sess.post(url, data=json.dumps(doc))
    resp.raise_for_status()

    result = resp.json()
    proc = Process(pid=result['pid'],
                   spec=doc, host=host)
    db.session.add(proc)
    db.session.commit()
    return jsonify({'created': proc.id})


@app.route('/files/<path>', methods=['PUT', 'GET'])
def files(path):
    storage = FileStorage(app.config['STORAGE_DIR'])

    if request.method == 'PUT':
        storage.save(path, request.stream)
        resp = app.make_response('Updated %s' % path)
        resp.status_code = 202
        return resp

    return send_file(storage.read(path))
