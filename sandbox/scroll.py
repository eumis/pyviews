from pyviews.viewmodel.base import ViewModel
from pyviews.api.view import scroll_to, find_node

# pylint: disable=E1101
class ScrollVm(ViewModel):
    def __init__(self):
        ViewModel.__init__(self)
        self.items = range(100)

    def get_node_id(self, index):
        return 'item' + str(index)

    def scroll_to(self, index):
        node_id = self.get_node_id(index)
        scroll_to(find_node('scroll_id'), node_id)
