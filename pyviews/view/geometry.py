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
    def apply(self, widget):
        widget.grid(**self._args)

class PackGeometry(Geometry):
    def apply(self, widget):
        widget.pack(**self._args)
