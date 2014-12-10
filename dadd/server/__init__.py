import cherrypy

from cherrypy.process.plugins import Monitor


class Heartbeat(Monitor):

    def start(self):
        self.callback()
        super(Heartbeat, self).start()


def transform_config(config):
    """Take a flask config items to create a cherrypy/cheroot server
    config."""

    cp_conf = {
        'server.socket_host': str(config.get('HOST', '0.0.0.0')),
        'server.socket_port': int(config.get('PORT', 5000)),
    }

    if not config.get('DEBUG'):
        # Turn off any debugging settings
        cp_conf['engine.autoreload.on'] = False

    return cp_conf


def mount(app, path):
    cherrypy.tree.graft(app, path)


def run(config):
    config = transform_config(config)
    cherrypy.config.update(config)
    cherrypy.engine.signals.subscribe()
    cherrypy.engine.start()
    cherrypy.engine.block()


def monitor(name, func, interval):
    monitor = Heartbeat(cherrypy.engine, func, interval, name)
    monitor.subscribe()
