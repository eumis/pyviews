from tkinter import Canvas, TclError
from pyviews.core.node import Node

class CanvasNode(Node):
    def __init__(self, master: Canvas, xml_node, parent_context=None):
        super().__init__(xml_node, parent_context)
        self._canvas = master
        self._item_id = None
        self._rendered = False
        self._corner = None
        self._size = []
        self._place = None
        self._options = {}
        self._events = {}

    @property
    def place(self):
        return self._place

    @place.setter
    def place(self, value):
        self._place = value

    def set_attr(self, key, value):
        if hasattr(self, key):
            setattr(self, key, value)
        elif self._rendered:
            try:
                self._canvas.itemconfig(self._item_id, **{key: value})
            except TclError:
                pass
        else:
            self._options[key] = value

    def render(self):
        self._rendered = True
        self._item_id = self._create()
        self._options = None
        for event, command in self._events.items():
            self._canvas.tag_bind(self._item_id, '<' + event + '>', command)
        self._events = None

    def _create(self):
        raise '_create of CanvasItem is not implemented'

    def bind(self, event, command):
        if self._rendered:
            self._canvas.tag_bind(self._item_id, '<' + event + '>', command)
        else:
            self._events[event] = command

    def destroy(self):
        self._canvas.delete(self._item_id)

class Rectangle(CanvasNode):
    def __init__(self, master, xml_node, parent_context=None):
        super().__init__(master, xml_node, parent_context)

    def _create(self):
        return self._canvas.create_rectangle(*self._place, **self._options)

class Text(CanvasNode):
    def __init__(self, master, xml_node, parent_context=None):
        super().__init__(master, xml_node, parent_context)

    def _create(self):
        return self._canvas.create_text(*self._place, **self._options)

class Image(CanvasNode):
    def __init__(self, master, xml_node, parent_context=None):
        super().__init__(master, xml_node, parent_context)

    def _create(self):
        return self._canvas.create_image(*self._place, **self._options)

class Arc(CanvasNode):
    def __init__(self, master, xml_node, parent_context=None):
        super().__init__(master, xml_node, parent_context)

    def _create(self):
        return self._canvas.create_arc(*self._place, **self._options)

class Bitmap(CanvasNode):
    def __init__(self, master, xml_node, parent_context=None):
        super().__init__(master, xml_node, parent_context)

    def _create(self):
        return self._canvas.create_bitmap(*self._place, **self._options)

class Line(CanvasNode):
    def __init__(self, master, xml_node, parent_context=None):
        super().__init__(master, xml_node, parent_context)

    def _create(self):
        return self._canvas.create_line(*self._place, **self._options)

class Oval(CanvasNode):
    def __init__(self, master, xml_node, parent_context=None):
        super().__init__(master, xml_node, parent_context)

    def _create(self):
        return self._canvas.create_oval(*self._place, **self._options)

class Polygon(CanvasNode):
    def __init__(self, master, xml_node, parent_context=None):
        super().__init__(master, xml_node, parent_context)

    def _create(self):
        return self._canvas.create_polygon(*self._place, **self._options)

class Window(CanvasNode):
    def __init__(self, master, xml_node, parent_context=None):
        super().__init__(master, xml_node, parent_context)

    def _create(self):
        return self._canvas.create_window(*self._place, **self._options)

def render(node: CanvasNode):
    node.render()
