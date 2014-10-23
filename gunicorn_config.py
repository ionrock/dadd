# Config file for passing in on the gunicorn command line.
import os

bind = '0.0.0.0:' + str(os.environ.get('PORT', 8000))
workers = 4
loglevel = 'info'
accesslog = '-'
errorlog = '-'
syslog = True
timeout = 60
