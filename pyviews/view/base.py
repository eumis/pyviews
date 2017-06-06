class CompileNode:
    def __init__(self):
        self._xml_node = None
        self._context = {}
        self._watchers = []
        self._nodes = []
        self.view_model = None

    def set_xml_node(self, node):
        self._xml_node = node

    def xml_attrs(self):
        return self._xml_node.items()

    def get_text(self):
        return self._xml_node.text.strip()

    def get_children(self):
        return [NodeChild(xml_node, self.view_model) for xml_node in list(self._xml_node)]

    def has_attr(self, name):
        return hasattr(self, name)

    def set_attr(self, name, value):
        setattr(self, name, value)

    def set_context(self, key, value=None):
        if isinstance(key, dict):
            self._context = {**self._context, **key}
        else:
            self._context[key] = value

    def get_context(self):
        return self._context

    def clear(self):
        for child in self._nodes:
            child.destroy()
        self._nodes = []

    def destroy(self):
        self.clear()
        for watcher in self._watchers:
            watcher.dispose()

    def render(self, render_children):
        self.clear()
        self._nodes = render_children(self)

    def get_container_for_child(self):
        return None

    def get_widget(self):
        return None

    def add_watcher(self, watcher):
        self._watchers.append(watcher)

class NodeChild:
    def __init__(self, xml_node, view_model=None):
        self.xml_node = xml_node
        self.view_model = view_model

def get_handler(command):
    return lambda e, com=command: com()

class Watcher:
    def __init__(self, view_model, key, handler):
        self.dispose = lambda: view_model.release_callback(key, handler)
