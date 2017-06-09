from inspect import getfullargspec
from pyviews.common.values import EVENT_KEY

class CompileNode:
    def __init__(self):
        self._xml_node = None
        self._context = {}
        self._watchers = []
        self._nodes = []
        self.view_model = None
        self.context = NodeContext()

    def set_xml_node(self, node):
        self._xml_node = node

    def xml_attrs(self):
        return self._xml_node.items()

    def get_xml_children(self):
        return [NodeChild(xml_node, self.view_model) for xml_node in list(self._xml_node)]

    def get_text(self):
        return self._xml_node.text.strip() if self._xml_node.text else ''

    def has_attr(self, name):
        return hasattr(self, name)

    def set_attr(self, name, value):
        setattr(self, name, value)

    def bind(self, event, command):
        pass

    def config(self, key, value):
        pass

    def clear(self):
        for child in self._nodes:
            child.destroy()
        self._nodes = []

    def destroy(self):
        self.clear()
        for watcher in self._watchers:
            watcher.dispose()

    def render(self, render_children, parent=None):
        self.clear()
        self._nodes = render_children(self)

    def get_widget_master(self):
        return None

    def get_widget(self):
        return None

    def add_watcher(self, watcher):
        self._watchers.append(watcher)

    def row_config(self, row, args):
        widget = self.get_widget_master()
        if not widget:
            return
        widget.rowconfigure(row, **args)

    def col_config(self, col, args):
        widget = self.get_widget_master()
        if not widget:
            return
        widget.columnconfigure(col, **args)

class NodeChild:
    def __init__(self, xml_node, view_model=None):
        self.xml_node = xml_node
        self.view_model = view_model

# pylint: disable=W1505
# https://docs.python.org/3/library/inspect.html#inspect.getfullargspec
def get_handler(command):
    spec = getfullargspec(command)
    arg = spec[0][0] if spec[0] else ''
    if arg == EVENT_KEY:
        return lambda e, com=command: com(e)
    else:
        return lambda e, com=command: com()

class Watcher:
    def __init__(self, view_model, key, handler):
        self.dispose = lambda: view_model.release_callback(key, handler)

class NodeContext:
    def __init__(self, source=None):
        self.globals = source.globals.copy() if source else {}
        self.styles = source.styles.copy() if source else {}
