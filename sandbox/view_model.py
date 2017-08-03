from pyviews.viewmodel.base import ViewModel

class AppViewModel(ViewModel):
    def __init__(self):
        super().__init__()
        self.view = 'changepage'
