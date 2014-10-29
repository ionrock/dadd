from flask import jsonify, request

from dad.master import app
from dad.master.models import db, Host


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
