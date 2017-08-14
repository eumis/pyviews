class CompileContext:
    def __init__(self, xml_node=None, parent=None, master=None):
        self._node = None
        self.xml_node = xml_node
        self.parent_node = parent
        self.master_widget = master
        self.globals = {}

    @property
    def node(self):
        return self._node

    @node.setter
    def node(self, value):
        if self._node:
            self._node.destroy()
        self._node = value
