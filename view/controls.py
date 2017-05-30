from view.tree import View

class For(View):
    def __init__(self, parent_widget):
        View.__init__(self, parent_widget)

    def get_xml_children(self):
        return list(self._node)
    
class ItemViewModel(ViewModel)
