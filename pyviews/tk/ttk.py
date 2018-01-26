from tkinter.ttk import Style
from pyviews.core.ioc import inject
from pyviews.tk.widgets import WidgetNode

class TtkWidgetNode(WidgetNode):
    @property
    def style(self):
        return self._style

    @style.setter
    @inject('container')
    def style(self, value, container=None):
        if not self._style:
            ttk_style = Style()
            self._style = StyleWrapper
        container.get('apply_styles')(self, self._style)

class StyleWrapper:
    def __init__(self, name):
        self._name = name
        self._style = Style()

    def set_attr(self, key, value):
        pass
