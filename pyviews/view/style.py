from pyviews.view.base import CompileNode

class Style(CompileNode):
    def __init__(self, *args):
        super().__init__()
        self.name = None
        self._attrs = {}

    def set_attr(self, name, value):
        if hasattr(self, name):
            setattr(self, name, value)
        else:
            self._attrs[name] = (name, value)

    def get_attrs(self):
        return self._attrs
