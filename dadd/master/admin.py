from flask.ext.admin import Admin
from flask.ext.admin.contrib.sqla import ModelView

from dadd.master import models


def admin(app):
    admin = Admin(app)
    session = models.db.session
    admin.add_view(ModelView(models.Process, session))
    admin.add_view(ModelView(models.Host, session))
    admin.add_view(ModelView(models.Logfile, session))
