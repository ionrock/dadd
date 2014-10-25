from flask import send_file, request, jsonify

from dad.master import app
from dad.master.files import FileStorage
from dad.master.models import db, Host


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


@app.route('/files/<path>', methods=['PUT', 'GET'])
def files(path):
    storage = FileStorage(app.config['STORAGE_DIR'])

    if request.method == 'PUT':
        storage.save(path, request.stream)
        resp = app.make_response('Updated %s' % path)
        resp.status_code = 202
        return resp

    return send_file(storage.read(path))
