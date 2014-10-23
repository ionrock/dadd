import os

from subprocess import call

from dad.master.models import db


HERE = os.path.dirname(os.path.abspath(__file__))

if __name__ == '__main__':
    sql_file = os.path.join(HERE, 'dbsetup.sql')
    dbsetup = 'psql -U postgres -h localhost -f %s' % sql_file
    call(dbsetup.split())
    db.create_all()
    print('Tables created')
