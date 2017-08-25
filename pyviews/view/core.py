from tkinter import Tk, Widget
from pyviews.view.base import CompileNode
from pyviews.common.reflection import get_handler
from pyviews.common.compiling import CompileContext

class App(CompileNode):
    def __init__(self):
        super().__init__()
        self.root = Tk()
        self.root.bind_all('<Button-1>', lambda e: prop_focus(e.widget), '+')

    @property
    def state(self):
        return self.root.state()

    @state.setter
    def state(self, state):
        self.root.state(state)

    def bind(self, event, command):
        self.root.bind('<'+event+'>', get_handler(command))

    def set_attr(self, name, value):
        if hasattr(self, name):
            setattr(self, name, value)
        elif hasattr(self.root, name):
            setattr(self.root, name, value)
        else:
            self.root.configure(**{name:value})

    def create_compile_context(self, xml_node):
        return CompileContext(xml_node, self, self.root)

    def run(self):
        self.root.mainloop()

def prop_focus(widget):
    if not isinstance(widget, Widget):
        return
    elif widget['takefocus'] == '1':
        widget.focus_set()
    elif widget.master:
        prop_focus(widget.master)

class WidgetNode(CompileNode):
    def __init__(self, widget):
        super().__init__()
        self.widget = widget
        self._geometry = None

    @property
    def geometry(self):
        return self._geometry

    @geometry.setter
    def geometry(self, value):
        self._geometry = value
        if self._geometry:
            self._geometry.apply(self.widget)

    def bind(self, event, command):
        self.widget.bind('<'+event+'>', get_handler(command))

    def set_attr(self, name, value):
        if hasattr(self, name):
            setattr(self, name, value)
        elif hasattr(self.widget, name):
            setattr(self.widget, name, value)
        else:
            self.widget.configure(**{name: value})

    def destroy(self):
        super().destroy()
        self.widget.destroy()

    def create_compile_context(self, xml_node):
        return CompileContext(xml_node, self, self.widget)

class Container(CompileNode):
    def __init__(self, master):
        super().__init__()
        self._master = master

    def set_attr(self, name, value):
        if hasattr(self, name):
            setattr(self, name, value)

    def create_compile_context(self, xml_node):
        return CompileContext(xml_node, self, self._master)
