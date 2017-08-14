from pyviews.common.compiling import CompileContext

class CompileNode:
    def __init__(self):
        self._destroy = []
        self._nodes = []
        self._node_id = ''
        self.xml_node = None
        self.view_model = None
        self.context = NodeContext()

    @property
    def node_id(self):
        return self._node_id

    @node_id.setter
    def node_id(self, value):
        if value == self._node_id:
            return
        self._clear_node_id()
        self._node_id = value
        CompileNode.nodes[self._node_id] = self

    def _clear_node_id(self):
        if self._node_id:
            del CompileNode.nodes[self._node_id]

    def has_attr(self, name):
        return hasattr(self, name)

    def set_attr(self, name, value):
        setattr(self, name, value)

    def destroy(self):
        self.clear()
        self._clear_node_id()
        for callback in self._destroy:
            callback()

    def clear(self):
        for child in self._nodes:
            child.destroy()
        self._nodes = []

    def render(self):
        self.clear()
        self._nodes = []
        try:
            for xml_node in list(self.xml_node):
                context = self.create_compile_context(xml_node)
                self._nodes.append(self.compile_xml(context))
        except RenderException:
            pass

    def create_compile_context(self, xml_node):
        return CompileContext(xml_node, self)

    def compile_xml(self, *args):
        raise RenderException('compile is not setup yet')

    def on_destroy(self, callback):
        self._destroy.append(callback)

CompileNode.nodes = {}

class NodeContext:
    def __init__(self, source=None):
        self.globals = source.globals.copy() if source else {}
        self.styles = source.styles.copy() if source else {}

class RenderException(Exception):
    pass
