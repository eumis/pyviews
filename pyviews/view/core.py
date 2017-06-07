from tkinter import Tk, Widget
from pyviews.view.base import CompileNode, get_handler

class App(CompileNode):
    def __init__(self):
        CompileNode.__init__(self)
        self._tk = Tk()
        self.state = None
        self._tk.bind_all('<Button-1>', lambda e: prop_focus(e.widget), '+')

    def get_container_for_child(self):
        return self._tk

    def get_widget(self):
        return self._tk

    def bind(self, event, command):
        self._tk.bind('<'+event+'>', get_handler(command))

    def has_attr(self, name):
        return hasattr(self, name) or hasattr(self._tk, name)

    def set_attr(self, name, value):
        attr_inst = self if hasattr(self, name) else self._tk
        setattr(attr_inst, name, value)

    def render(self, render_children):
        if self.state:
            self._tk.state(self.state)
        super().render(render_children)

    def config(self, key, value):
        self._tk.configure({key: value})

    def run(self):
        self._tk.mainloop()

class WidgetNode(CompileNode):
    def __init__(self, widget):
        CompileNode.__init__(self)
        self._widget = widget
        self.geometry = None

    def get_container_for_child(self):
        return self._widget

    def get_widget(self):
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

    def destroy(self):
        super().destroy()
        self._widget.destroy()

    def config(self, key, value):
        self._widget.configure({key: value})

    def render(self, render_children):
        self.geometry.apply(self._widget)
        CompileNode.render(self, render_children)

class Container(CompileNode):
    def __init__(self, parent_widget):
        CompileNode.__init__(self)
        self._parent_widget = parent_widget

    def get_container_for_child(self):
        return self._parent_widget

def prop_focus(widget):
    if not isinstance(widget, Widget):
        return
    if widget['takefocus'] == '1':
        widget.focus_set()
    elif widget.master:
        prop_focus(widget.master)
