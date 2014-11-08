class mount(object):
    def __init__(self, app, route, methods=None):
        self.methods = methods or [
            'GET', 'POST', 'PUT', 'HEAD', 'DELETE', 'PATCH'
        ]
        self.app = app
        self.route = route

    def _add_route(self, obj, meth):
        view = getattr(obj, meth, None)
        if view:
            self.app.route(self.route, methods=[meth])(view)

    def __call__(self, cls):
        obj = cls()

        for meth in self.methods:
            self._add_route(obj, meth)
