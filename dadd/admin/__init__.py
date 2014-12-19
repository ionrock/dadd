from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

from dadd.master import app
from dadd.master.models import db
from dadd.master.utils import update_config


def manage():
    update_config(app)
    Migrate(app, db)
    manager = Manager(app)
    manager.add_command('db', MigrateCommand)
    manager.run()
