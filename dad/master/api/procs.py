import json

from flask import jsonify, request, make_response

from dad.master import app
from dad.master.utils import get_session, find_host
from dad.master.models import db, Process, Logfile


def set_proc_state(id, state):
    proc = Process.query.get(id)
    proc.state = state
    db.session.add(proc)
    db.session.commit()


@app.route('/api/procs/<id>/', methods=['GET'])
def proc_view(id):
    proc = Process.query.get(id)

    return jsonify({
        'id': proc.id,
        'host': {
            'uri': 'http://%s' % str(proc.host)
        },
        'spec': proc.spec,
        'state': proc.state,
    })


@app.route('/api/procs/<id>/<state>/', methods=['POST'])
def proc_state_init(id, state):
    set_proc_state(id, state)
    return jsonify({'status': state})


@app.route('/api/procs/<id>/logfile/', methods=['GET', 'POST'])
def proc_logfile(id):
    proc = Process.query.get(id)
    if request.method == 'GET':
        if proc.logfile_id:
            return make_response(proc.logfile.content)
        return 'No logfile found', 404

    app.logger.info(request.data)

    logfile = Logfile(content=request.data)
    proc.logfile = logfile
    db.session.add(logfile)
    db.session.add(proc)
    db.session.commit()
    return jsonify({'message': 'added logfile'})


# Start an app
@app.route('/api/procs/', methods=['POST'])
def proc_create():
    doc = request.json

    # Find a host
    host = find_host()

    # Create our process in the DB
    proc = Process(spec=doc, host=host)
    db.session.add(proc)
    db.session.commit()

    # Add the ID to the spec
    doc['process_id'] = proc.id

    # Try creating the process via the host
    url = 'http://%s/run/' % str(host)
    sess = get_session()
    print('Creating app on host: %s' % url)
    resp = sess.post(url, data=json.dumps(doc))
    resp.raise_for_status()

    # Save the pid
    result = resp.json()
    proc.pid = result['pid']
    db.session.add(proc)
    db.session.commit()

    return jsonify({'created': proc.id})


@app.route('/api/procs/', methods=['GET'])
def proc_list():
    procs = Process.query.all()
    doc = {
        'procs': [],
        'next': None,
        'prev': None,
    }
    for proc in procs:
        doc['procs'].append(proc.as_dict())

    return jsonify(doc)
