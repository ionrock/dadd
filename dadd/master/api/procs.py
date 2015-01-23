from flask import jsonify, request, make_response, abort

from dadd.master import app
from dadd.master.models import db, Process, Logfile

from sqlalchemy import desc


def set_proc_state(pid, state):
    proc = Process.query.get(pid)
    if not proc:
        app.logger.error('Error settings state %s. Pid %s not found' % (state, pid))
        abort(404)
    proc.state = state
    db.session.add(proc)
    db.session.commit()


@app.route('/api/procs/<pid>/', methods=['GET'])
def proc_view(pid):
    proc = Process.query.get(pid)

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
    if not doc:
        resp = jsonify({'message': 'A specification doc must be provided'})
        resp.status_code = 400
        return resp

    proc = Process.create(doc)
    if not proc:
        resp = jsonify({
            'message': 'Error creating process'
        })
        resp.status_code = 404
        return resp

    return jsonify({'message': {
        'success': True,
        'process': '/api/procs/%s' % proc.id
    }})


@app.route('/api/procs/', methods=['GET'])
def proc_list():
    procs = Process.query.order_by(desc(Process.start_time)).all()
    doc = {
        'procs': [],
        'next': None,
        'prev': None,
    }
    for proc in procs:
        doc['procs'].append(proc.as_dict())

    return jsonify(doc)
