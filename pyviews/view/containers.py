from pyviews.view.core import Container
from pyviews.view.base import NodeChild
from pyviews.viewmodel.base import ViewModel

class For(Container):
    def __init__(self, parent_widget):
        Container.__init__(self, parent_widget)
        self._items = []
        self._render_children = None

    def get_children(self):
        children = []
        for index, item in enumerate(self.items):
            item_vm = ItemViewModel(item, self.view_model, index)
            children += [NodeChild(xml_node, item_vm) for xml_node in list(self._xml_node)]
        return children

    @property
    def items(self):
        return self._items

    @items.setter
    def items(self, val):
        self._items = val if val else []
        self.render()

    def render(self, render_children=None):
        self._render_children = render_children if render_children else self._render_children
        if self._render_children:
            super().render(self._render_children)

class ItemViewModel(ViewModel):
    def __init__(self, item, parent, index):
        ViewModel.__init__(self)
        self.item = item
        self.parent = parent
        self.index = index
