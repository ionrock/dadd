import json

from flask import jsonify, request

from dad.master import app
from dad.master.utils import get_session, find_host
from dad.master.models import db, Process, Logfile


def set_proc_state(id, state):
    proc = Process.query.get(id)
    proc.state = state
    db.session.add(proc)
    db.session.commit()


@app.route('/api/procs/<id>/<state>/', methods=['POST'])
def proc_state_init(id, state):
    set_proc_state(id, state)
    return jsonify({'status': state})


@app.route('/api/procs/<id>/logfile/', methods=['GET', 'POST'])
def proc_logfile(id):
    proc = Process.query.get(id)
    if request.method == 'GET':
        if proc.logfile:
            return proc.logfile.content
        return 'No logfile found', 404

    logfile = Logfile(content=request.content)
    proc.logfile = logfile
    db.add(logfile)
    db.add(proc)
    db.commit()


# Start an app
@app.route('/api/procs/', methods=['POST'])
def proc_create():
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
                   spec=doc,
                   host=host)
    db.session.add(proc)
    db.session.commit()
    return jsonify({'created': proc.id})
