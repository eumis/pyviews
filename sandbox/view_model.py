from pyviews.viewmodel.base import ViewModel

class AppViewModel(ViewModel):
    def __init__(self, default_view=None):
        super().__init__()
        self.view = default_view
