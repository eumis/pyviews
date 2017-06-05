class CompileNode:
    def __init__(self):
        self._node = None
        self._context = {}
        self.view_model = None

    def set_node(self, node):
        self._node = node

    def xml_attrs(self):
        return self._node.items()

    def get_text(self):
        return self._node.text.strip()

    def get_children(self):
        return [NodeChild(xml_node, self.view_model) for xml_node in list(self._node)]

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
        pass

    def destroy(self):
        pass

    def render(self, render_children):
        render_children(self)

    def get_container_for_child(self):
        return None

    def get_widget(self):
        return None

class NodeChild:
    def __init__(self, xml_node, view_model=None):
        self.xml_node = xml_node
        self.view_model = view_model

def get_handler(command):
    return lambda e, com=command: com()
