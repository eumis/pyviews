from pyviews.core.observable import ObservableEnt

# pylint: disable=E1101
class ScrollVm(ObservableEnt):
    def __init__(self):
        super().__init__()
        self.items = [ScrollItem(i) for i in range(100)]

    def get_node_id(self, index):
        return 'item' + str(index)

    def scroll_to(self, index):
        node_id = self.get_node_id(index)
        # scroll_to(find_node('scroll_id'), node_id)

class ScrollItem(ObservableEnt):
    def __init__(self, index):
        super().__init__()
        self._index = index
        self.text = str(self._index)

    def add(self):
        self.text = self.text + str(self._index)
