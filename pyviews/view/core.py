from tkinter import Tk
from pyviews.view.base import CompileNode, get_handler

class App(CompileNode):
    def __init__(self):
        CompileNode.__init__(self)
        self._tk = Tk()
        self.state = None

    def get_container_for_child(self):
        return self._tk

    def bind(self, event, command):
        self._tk.bind('<'+event+'>', get_handler(command))

    def has_attr(self, name):
        return hasattr(self, name) or hasattr(self._tk, name)

    def set_attr(self, name, value):
        attr_inst = self if hasattr(self, name) else self._tk
        setattr(attr_inst, name, value)

    def clear(self):
        for widget in self._tk.winfo_children():
            widget.destroy()

    def render(self, render_children):
        if self.state:
            self._tk.state(self.state)
        render_children(self)

    def run(self):
        self._tk.mainloop()

class WidgetNode(CompileNode):
    def __init__(self, widget):
        CompileNode.__init__(self)
        self._widget = widget
        self._grid_args = {}

    def get_container_for_child(self):
        return self._widget

    def bind(self, event, command):
        self._widget.bind('<'+event+'>', get_handler(command))

    def has_attr(self, name):
        return True

    def set_attr(self, name, value):
        if hasattr(self, name):
            setattr(self, name, value)
        elif hasattr(self._widget, name):
            setattr(self._widget, name, value)

    def clear(self):
        for widget in self._widget.winfo_children():
            widget.destroy()

    def destroy(self):
        self._widget.destroy()

    def grid(self, key, value):
        self._grid_args[key] = value

    def config(self, key, value):
        self._widget.configure({key: value})

    def render(self, render_children):
        self._widget.grid(self._grid_args)
        CompileNode.render(self, render_children)

class Container(CompileNode):
    def __init__(self, parent_widget):
        CompileNode.__init__(self)
        self._parent_widget = parent_widget
        self._widgets = None

    def get_container_for_child(self):
        return self._parent_widget

    def render(self, render_children):
        self._widgets = render_children(self)

    def clear(self):
        if self._widgets:
            for widget in self._widgets:
                widget.destroy()
            self._widgets = None
            