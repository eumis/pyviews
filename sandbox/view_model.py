from pyviews.core.observable import ObservableEnt

class AppViewModel(ObservableEnt):
    def __init__(self, default_view=None):
        super().__init__()
        self.view = default_view
