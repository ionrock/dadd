from flask import jsonify, request, url_for

from dadd.master import app
from dadd.master.models import db, Host


# Host Registration
@app.route('/api/hosts/', methods=['POST'])
def api_register_host():
    doc = request.json
    host = Host(host=doc['host'], port=doc['port'])
    host_uri = url_for('api_view_host', id_or_name=str(host))
    query = db.session.query(Host).filter_by(
        host=host.host, port=host.port
    )
    if not query.count():
        db.session.add(host)
        db.session.commit()
        return jsonify({'created': host_uri})
    return jsonify({'exists': host_uri})


@app.route('/api/hosts/', methods=['GET'])
def api_view_hosts():
    hosts = Host.query.all()
    return jsonify({
        'hosts': [str(host) for host in hosts]
    })


def find_host(id_or_name):
    if ':' in id_or_name:
        hostname, port = id_or_name.split(':', 1)
        return db.session.query(Host).filter_by(
            host=hostname, port=port
        ).first()

    return db.sesssion.query(Host).get(id=id_or_name)


@app.route('/api/hosts/<id_or_name>/', methods=['GET'])
def api_view_host(id_or_name):
    host = find_host(id_or_name)
    doc = {
        'host': host.host,
        'port': host.port,
        'uri': 'http://%s' % host,
        'processes': {
            process.id: {
                'cmd': process.spec['cmd'],
                'logfile': '/api/procs/%s/logfile/' % process.id,
                'state': process.state,
            }
            for process in host.procs
            if not process.end_time
        }
    }
    return jsonify(doc)


@app.route('/api/hosts/<id_or_name>/', methods=['DELETE'])
def api_delete_host(id_or_name):
    host = find_host(id_or_name)
    if not host:
        return 'Not Found', 404

    db.session.delete(host)
    return jsonify({'deleted': str(host)})
