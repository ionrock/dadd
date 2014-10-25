from dad.master import app

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

    state = db.Column(db.Enum(
        'init', 'setup', 'running', 'failed', 'success',
        name='proc_state'
    ))


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
