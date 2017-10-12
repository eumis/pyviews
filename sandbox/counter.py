from pyviews.core.observable import ObservableEnt

class Counter(ObservableEnt):
    def __init__(self):
        super().__init__()
        self.count = 0

    def up_count(self):
        self.count += 1
