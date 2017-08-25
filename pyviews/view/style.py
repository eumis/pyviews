from pyviews.view.base import CompileNode
from pyviews.view.containers import View

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

class Styles(View):
    def __init__(self):
        super().__init__()
        self._styles = {}

    def compile_children(self):
        super().compile_children()
        self._styles = {}
        for node in self._nodes:
            self._styles.update(node.context.styles)

    def get_styles(self):
        return self._styles
