from pyviews.view.base import CompileNode
from pyviews.view.core import Container
from pyviews.application import load_styles

class Styles(Container):
    def __init__(self):
        super().__init__(None)

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

    def render(self, render_children, parent=None):
        apply_style = self.apply
        if self.path:
            styles = load_styles(self.path)
            key = self.path_name if self.path_name else self.name
            if key in styles:
                apply_style = lambda node: merge_styles(node, styles[key], self.apply)
        if parent and self.name:
            parent.context.styles[self.name] = apply_style

    def apply(self, node):
        if self.geometry:
            node.geometry = self.geometry
        for key, value in self._config.items():
            node.config(key, value)
        for event, command in self._bind.items():
            node.bind(event, command)

def merge_styles(node, one, two):
    one(node)
    two(node)
