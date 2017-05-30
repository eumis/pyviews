from common.values import EVENT_KEY

class CompileNode:
    def __init__(self):
        self._node = None
        self._context = {}
        self.view_model = None

    def set_node(self, node):
        self._node = node

    def get_view_model(self):
        return self.view_model

    def xml_attrs(self):
        return self._node.items()

    def get_text(self):
        return self._node.text.strip()

    def get_xml_children(self):
        return list(self._node)

    def has_attr(self, name):
        return hasattr(self, name)

    def set_attr(self, name, value):
        setattr(self, name, value)

    def set_context(self, key, value=None):
        if isinstance(key, dict):
            self._context = {**self._context, **key}
        else:
            self._context[key] = value

    def get_context(self):
        return self._context

    def clear(self):
        pass

    def render(self):
        pass

    def get_container_for_child(self):
        return None

class View(CompileNode):
    def __init__(self, parent_widget):
        CompileNode.__init__(self)
        self._parent_widget = parent_widget

    def get_container_for_child(self):
        return self._parent_widget

class WidgetNode(CompileNode):
    def __init__(self, widget):
        CompileNode.__init__(self)
        self._widget = widget
        self.grid_row = None
        self.grid_column = None

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
        else:
            self._widget.configure(**{name:value})

    def clear(self):
        for widget in self._widget.winfo_children():
            widget.destroy()

    def render(self):
        self._widget.grid(row=int(self.grid_row), column=int(self.grid_column))

class AppNode(CompileNode):
    def __init__(self, tk):
        CompileNode.__init__(self)
        self._tk = tk

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

    def run(self):
        self._tk.mainloop()

def get_handler(command):
    return lambda e, com=command: com()
