from pyviews.view.base import CompileNode
from pyviews.view.core import Container

class Style(CompileNode):
    def __init__(self, parent_widget):
        super().__init__()
        self._parent_widget = parent_widget
        self._config = {}
        self._bind = {}
        self.name = None
        self.path = None
        self.path_name = None
        self.geometry = None

    def get_widget_master(self):
        return self._parent_widget

    def config(self, key, value):
        self._config[key] = value

    def bind(self, event, command):
        self._bind[event] = command

    def render(self):
        apply_style = self.apply
        if self.path:
            styles = load_styles(self.path)
            key = self.path_name if self.path_name else self.name
            if key in styles:
                apply_style = merge_styles(styles[key], self.apply)
        if parent and self.name:
            parent.context.styles[self.name] = apply_style

    def apply(self, node):
        if self.geometry:
            if node.geometry:
                node.geometry.merge(self.geometry)
            else:
                node.geometry = self.geometry
        for key, value in self._config.items():
            node.config(key, value)
        for event, command in self._bind.items():
            node.bind(event, command)

def merge_styles(one, two):
    return lambda node: apply_styles(node, one, two)

def apply_styles(node, one, two):
    one(node)
    two(node)
