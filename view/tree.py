class CompileNode:
    def __init__(self):
        self._node = None

    def set_node(self, node):
        self._node = node

    def items(self):
        return self._node.items()

class View(CompileNode):
    def __init__(self):
        CompileNode.__init__(self)

class WidgetNode(CompileNode):
    def __init__(self, widget):
        CompileNode.__init__(self)
        self._widget = widget
