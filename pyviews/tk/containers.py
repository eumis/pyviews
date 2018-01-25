from pyviews.core.ioc import inject
from pyviews.core.xml import XmlNode
from pyviews.core.compilation import InheritedDict
from pyviews.core.node import Node
from pyviews.tk.widgets import WidgetArgs
from pyviews.tk.views import get_view_root

class Container(Node):
    def __init__(self, master, xml_node: XmlNode, parent_context=None):
        super().__init__(xml_node, parent_context)
        self.master = master

    @property
    def view_model(self):
        try:
            return self.globals['vm']
        except KeyError:
            return None

    @view_model.setter
    def view_model(self, value):
        self.globals['vm'] = value

    def set_attr(self, key, value):
        setattr(self, key, value)

    def get_node_args(self, xml_node):
        return WidgetArgs(xml_node, self, self.master)

class View(Container):
    def __init__(self, master, xml_node: XmlNode, parent_context=None):
        super().__init__(master, xml_node, parent_context)
        self._name = None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if self._name == value:
            return
        self._name = value
        self.parse_children()

    @inject('parse')
    def parse_children(self, parse=None):
        self.destroy_children()
        try:
            root_xml = get_view_root(self.name)
            self._child_nodes = [parse(root_xml, self.get_node_args(root_xml))]
        except FileNotFoundError:
            self._child_nodes = []

class For(Container):
    def __init__(self, master, xml_node: XmlNode, parent_context=None):
        super().__init__(master, xml_node, parent_context)
        self._items = []
        self._rendered = False
        self._child_count = 0

    @property
    def items(self):
        return self._items

    @items.setter
    def items(self, val):
        self._items = val
        if self._rendered:
            self._destroy_overflow()
            self._update_existing()
            self._create_not_existing()

    def _destroy_overflow(self):
        try:
            items_count = len(self._items)
            children_count = self._child_count * items_count
            overflow = self._child_nodes[children_count:]
            for child in overflow:
                child.destroy()
            self._child_nodes = self._child_nodes[:children_count]
        except IndexError:
            pass

    def _update_existing(self):
        try:
            for index, item in enumerate(self._items):
                start = index * self._child_count
                end = (index + 1) * self._child_count
                for child_index in range(start, end):
                    globs = self._child_nodes[child_index].globals
                    globs['item'] = item
        except IndexError:
            pass

    def _create_not_existing(self):
        start = int(len(self._child_nodes) / self._child_count)
        end = len(self._items)
        self._create_children([(i, self._items[i]) for i in range(start, end)])

    @inject('parse')
    def _create_children(self, items, parse=None):
        nodes = self.xml_node.get_children()
        for index, item in items:
            for xml_node in nodes:
                args = self.get_node_args(xml_node, index, item)
                self._child_nodes.append(parse(xml_node, args))

    def parse_children(self):
        self._rendered = True
        self._child_count = len(self.xml_node.get_children())
        self.destroy_children()
        self._create_children([(i, item) for i, item in enumerate(self._items)])

    def get_node_args(self, xml_node: XmlNode, index=None, item=None):
        args = super().get_node_args(xml_node)
        context = args['parent_context'].copy()
        item_globals = InheritedDict(context['globals'])
        item_globals['index'] = index
        item_globals['item'] = item
        context['globals'] = item_globals
        args['parent_context'] = context
        return args

class If(Container):
    def __init__(self, master, xml_node: XmlNode, parent_context=None):
        super().__init__(master, xml_node, parent_context)
        self._condition = False
        self._rendered = False

    @property
    def condition(self):
        return self._condition

    @condition.setter
    def condition(self, value):
        if self._condition == value:
            return
        self._condition = value
        if self._rendered:
            self.destroy_children()
            self.parse_children()

    def parse_children(self):
        if self._condition:
            super().parse_children()
        self._rendered = True
