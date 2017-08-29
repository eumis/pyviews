from pyviews.viewmodel.base import ViewModel
from pyviews.common.view import scroll_to, find_node

# pylint: disable=E1101
class ScrollVm(ViewModel):
    def __init__(self):
        super().__init__(self)
        self.items = range(1000)

    def get_node_id(self, index):
        return 'item' + str(index)

    def scroll_to(self, index):
        node_id = self.get_node_id(index)
        scroll_to(find_node('scroll_id'), node_id)
