from pyviews.viewmodel.base import ViewModel
from pyviews.view.base import CompileNode

class TestViewModel(ViewModel):
    def __init__(self):
        super().__init__()
        self.name = None
        self.value = None

class TestNode(CompileNode):
    pass

