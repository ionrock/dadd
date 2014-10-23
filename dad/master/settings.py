import os

curdir = os.getcwd()

DEBUG = True
SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://dadapp:uhpqZ5pc@localhost/daddb'
STORAGE_DIR = os.path.join(curdir, 'temp_file_storage')
