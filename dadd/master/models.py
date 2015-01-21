import json

from datetime import datetime

import requests

from dadd.master import app
from dadd.master.utils import get_session

from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.orm import relationship, backref


db = SQLAlchemy(app)


class Process(db.Model):

    __tablename__ = 'processes'

    id = db.Column(db.Integer, primary_key=True)
    pid = db.Column(db.Integer)
    spec = db.Column(JSON, nullable=False)
    host_id = db.Column(db.Integer, db.ForeignKey('hosts.id'))
    host = relationship('Host', backref=backref('procs'),
                        cascade='all, delete')

    logfile_id = db.Column(db.Integer, db.ForeignKey('logfiles.id'))
    logfile = relationship('Logfile', backref=backref('process'))

    start_time = db.Column(db.DateTime, default=datetime.now)
    end_time = db.Column(db.DateTime)

    state = db.Column(db.Enum(
        'init', 'setup', 'running', 'failed', 'success',
        name='proc_state'
    ))

    def as_dict(self):
        return {
            'id': self.id,
            'pid': self.pid,
            'spec': self.spec,
            'host': self.host.as_dict() if self.host else '',
            # TODO: Use flask url generation
            'logfile': '/api/procs/%s/logfile/' % self.id,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'state': self.state,
            'update_state_uri': '/api/procs/%s/<state>/' % self.id
        }

    @classmethod
    def create(cls, spec):
        """
        Create a new process on a host.

        This will keep trying to start the process on a host until
        there are no hosts left to try. The Host.find_available SHOULD
        remove bad hosts that have shutdown or died so that this
        doesn't loop forever.
        """
        try:
            host = Host.find_available()
        except Exception as e:
            app.logger.error(e.message)
            return None

        # Create our process in the DB
        proc = cls(spec=spec, host=host)
        db.session.add(proc)
        db.session.commit()

        # Add the ID to the spec
        spec['process_id'] = proc.id

        try:
            sess = get_session()
            # Try creating the process via the host
            url = 'http://%s/run/' % str(host)
            app.logger.debug('Creating app on host: %s' % url)
            resp = sess.post(url, data=json.dumps(spec),
                             allow_redirects=False)
            resp.raise_for_status()

            # Save the pid
            result = resp.json()
        except requests.exceptions.HTTPError:
            return cls.create(spec)
        except requests.exceptions.ConnectionError as e:
            app.logger.error(e)
            return None

        proc.pid = result['pid']
        db.session.add(proc)
        db.session.commit()

        return proc


class Host(db.Model):
    __tablename__ = 'hosts'
    __table_args__ = (
        UniqueConstraint('host', 'port'),
    )

    id = db.Column(db.Integer, primary_key=True)
    host = db.Column(db.String, nullable=False)
    port = db.Column(db.Integer, nullable=False)

    def __str__(self):
        return '%s:%s' % (self.host, self.port)

    def as_dict(self):
        return {
            'id': self.id,
            'host': self.host,
            'port': self.port
        }

    @classmethod
    def find_available(cls):
        procs = 0
        current_host = None
        for host in db.session.query(cls).all():
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
            resp = requests.get('http://%s/up/' % str(current_host),
                                allow_redirects=False)

            # Check explicitly for a specific message in order to
            # easily filter out hosts that might have been taken over
            # by some other process at that port.
            assert resp.json()['worker_status'] == 'available'
            return current_host
        except Exception:
            db.session.delete(host)
            db.session.commit()
            return cls.find_available()


class Logfile(db.Model):
    __tablename__ = 'logfiles'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
