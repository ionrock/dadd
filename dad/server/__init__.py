import cherrypy

from cherrypy.process.plugins import Monitor


class Heartbeat(Monitor):

    def start(self):
        self.callback()
        super(Heartbeat, self).start()


def transform_config(config):
    """Take a flask config and update with the necessary
    cherrypy/cheroot equivalents."""

    config['server.socket_host'] = str(config.get('HOST', '0.0.0.0'))
    config['server.socket_port'] = int(config.get('PORT', 5000))

    return config


def mount(app, path):
    cherrypy.tree.graft(app, path)


def run(config):
    cherrypy.config.update(transform_config(config))
    cherrypy.engine.signals.subscribe()
    cherrypy.engine.start()
    cherrypy.engine.block()


def monitor(name, func, interval):
    monitor = Heartbeat(cherrypy.engine, func, interval, name)
    monitor.subscribe()
