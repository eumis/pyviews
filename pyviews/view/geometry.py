class Geometry:
    def __init__(self):
        self._args = {}

    def set(self, key, value):
        self._args[key] = value

    def items(self):
        return self._args.items()

    def merge(self, geometry):
        for key, value in geometry.items():
            self.set(key, value)

    def apply(self, widget):
        pass

class GridGeometry(Geometry):
    def __init__(self, row=None, col=None, **args):
        super().__init__()
        self._args = args if args else self._args
        self.set('row', row)
        self.set('column', col)

    def apply(self, widget):
        widget.grid(**self._args)

class PackGeometry(Geometry):
    def __init__(self, **args):
        super().__init__()

    def apply(self, widget):
        widget.pack(**self._args)
