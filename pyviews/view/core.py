from tkinter import Tk, Widget
from pyviews.view.base import CompileNode
from pyviews.common.reflection import get_handler
from pyviews.common.compiling import CompileContext

class App(CompileNode):
    def __init__(self):
        super().__init__()
        self._tk = Tk()
        self.state = None
        self._tk.bind_all('<Button-1>', lambda e: prop_focus(e.widget), '+')

    def bind(self, event, command):
        self._tk.bind('<'+event+'>', get_handler(command))

    def has_attr(self, name):
        return hasattr(self, name) or hasattr(self._tk, name)

    def set_attr(self, name, value):
        attr_inst = self if hasattr(self, name) else self._tk
        setattr(attr_inst, name, value)

    def render(self):
        if self.state:
            self._tk.state(self.state)
        super().render()

    def create_compile_context(self, xml_node):
        return CompileContext(xml_node, self, self._tk)

    def config(self, key, value):
        self._tk.configure({key: value})

    def run(self):
        self._tk.mainloop()

class WidgetNode(CompileNode):
    def __init__(self, widget):
        super().__init__()
        self._widget = widget
        self.geometry = None

    def bind(self, event, command):
        self._widget.bind('<'+event+'>', get_handler(command))

    def has_attr(self, name):
        return True

    def set_attr(self, name, value):
        if hasattr(self, name):
            setattr(self, name, value)
        elif hasattr(self._widget, name):
            setattr(self._widget, name, value)

    def destroy(self):
        super().destroy()
        self._widget.destroy()

    def config(self, key, value):
        self._widget.configure({key: value})

    def render(self):
        self.geometry.apply(self._widget)
        super().render()

    def create_compile_context(self, xml_node):
        return CompileContext(xml_node, self, self._widget)

    def row_config(self, row, args):
        self._widget.rowconfigure(row, **args)

    def col_config(self, col, args):
        self._widget.columnconfigure(col, **args)

class Container(CompileNode):
    def __init__(self, master):
        super().__init__()
        self._master = master

    def create_compile_context(self, xml_node):
        return CompileContext(xml_node, self, self._master)

def prop_focus(widget):
    if not isinstance(widget, Widget):
        return
    elif widget['takefocus'] == '1':
        widget.focus_set()
    elif widget.master:
        prop_focus(widget.master)
