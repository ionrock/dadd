from flask.ext.admin import Admin
from flask.ext.admin.contrib.sqla import ModelView

from dadd.master import models


class ProcessModelView(ModelView):
    # Make the latest first
    column_default_sort = ('start_time', True)

    def __init__(self, session):
        super(ProcessModelView, self).__init__(models.Process, session)


def admin(app):
    admin = Admin(app)
    session = models.db.session
    admin.add_view(ProcessModelView(session))
    admin.add_view(ModelView(models.Host, session))
    admin.add_view(ModelView(models.Logfile, session))
