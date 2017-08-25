from pyviews.common.ioc import inject
from pyviews.common.compiling import CompileContext

class CompileNode:
    @inject('compile_xml')
    def __init__(self, compile_xml=None):
        self._destroy = []
        self._nodes = []
        self._compile_xml = compile_xml
        self.xml_node = None
        self.view_model = None
        self.context = NodeContext()

    def destroy(self):
        self.remove_children()
        for callback in self._destroy:
            callback()

    def on_destroy(self, callback):
        self._destroy.append(callback)

    def remove_children(self):
        for child in self._nodes:
            child.destroy()
        self._nodes = []

    def compile_children(self):
        self.remove_children()
        for xml_node in list(self.xml_node):
            context = self.create_compile_context(xml_node)
            self._nodes.append(self._compile_xml(context))

    def create_compile_context(self, xml_node):
        return CompileContext(xml_node, self)

CompileNode.nodes = {}

class NodeContext:
    def __init__(self, source=None):
        self.globals = source.globals.copy() if source else {}
        self.styles = source.styles.copy() if source else {}

class RenderException(Exception):
    pass
