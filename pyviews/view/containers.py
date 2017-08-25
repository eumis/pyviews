from tkinter import Frame, Scrollbar, Canvas
from pyviews.view.base import CompileNode
from pyviews.view.core import Container
from pyviews.common.reflection import get_handler
from pyviews.common.compiling import CompileContext
from pyviews.common.parsing import parse_xml
from pyviews.common.ioc import inject

class For(Container):
    def __init__(self, master):
        Container.__init__(self, master)
        self._items = []
        self._rendered = False

    @property
    def items(self):
        return self._items

    @items.setter
    def items(self, val):
        self._items = val
        if self._rendered:
            self.compile_children()

    def compile_children(self):
        self._rendered = True
        self.remove_children()
        for index, item in enumerate(self._items):
            for xml_node in list(self.xml_node):
                context = self.create_compile_context(xml_node)
                context.globals['item'] = item
                context.globals['index'] = index
                self._nodes.append(self._compile_xml(context))

class View(Container):
    def __init__(self, master=None):
        super().__init__(master)
        self._path = None
        self._rendered = False

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        if value == self._path:
            return
        self._path = value
        view_nodes = list(self.xml_node)
        for xml_node in view_nodes:
            self.xml_node.remove(xml_node)
        self.xml_node.append(parse_xml(self._path))
        if self._rendered:
            self.compile_children()

    def compile_children(self):
        self._rendered = True
        super().remove_children()
        if self._path:
            super().compile_children()

class If(Container):
    def __init__(self, master):
        super().__init__(master)
        self._true = None
        self._false = None

    @property
    def true(self):
        return self._true

    @true.setter
    def true(self, value):
        if value != self._true:
            self._change_value(value)

    @property
    def false(self):
        return self._false

    @false.setter
    def false(self, value):
        if value != self._false:
            self._change_value(not value)

    def _change_value(self, true_value):
        self._true = true_value
        self._false = not true_value
        self.compile_children()

    def render(self):
        super().remove_children()
        if self._true:
            super().compile_children()

class Scroll(CompileNode):
    def __init__(self, master):
        self._frame = create_scroll_frame(master)
        self._canvas = create_canvas(self._frame)
        self._scroll = create_scroll(self._frame, self._canvas)
        self._container = create_container(self._canvas)
        self._container.bind('<Configure>', lambda event: self.config_container())
        self._canvas.bind('<Configure>', self.config_canvas)
        self._canvas.bind_all('<MouseWheel>', self.on_mouse_scroll)
        self._canvas.bind('<Enter>', lambda event: self.set_canvas_active())
        self._canvas.bind('<Leave>', lambda event: self.set_canvas_inactive())
        self._geometry = None
        self._style = None
        super().__init__()

    @property
    def style(self):
        return self._style

    @style.setter
    @inject('apply_style')
    def style(self, value, apply_style=None):
        self._style = value
        apply_style(self, value)

    @property
    def geometry(self):
        return self._geometry

    @geometry.setter
    def geometry(self, value):
        self._geometry = value
        if self._geometry:
            self._geometry.apply(self._frame)

    def config_container(self):
        self._canvas.config(scrollregion=self._canvas.bbox("all"))

    def config_canvas(self, event):
        self._canvas.itemconfig(self._container.win_id, width=event.width)

    def bind(self, event, command):
        handler = get_handler(command)
        self._container.bind('<'+event+'>', handler)
        if 'Button-' in event:
            self._canvas.bind('<'+event+'>', handler)

    def set_attr(self, name, value):
        if hasattr(self, name):
            setattr(self, name, value)
        elif hasattr(self._container, name):
            setattr(self._container, name, value)
        else:
            self._container.configure(**{name: value})
            if name == 'bg' or name == 'background':
                self._canvas.config(**{name: value})

    def on_mouse_scroll(self, event):
        if Scroll.active_canvas and self.is_active():
            Scroll.active_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def is_active(self):
        (up_offset, down_offset) = self._scroll.get()
        return not (up_offset == 0.0 and down_offset == 1.0)

    def set_canvas_active(self):
        Scroll.active_canvas = self._canvas

    def set_canvas_inactive(self):
        if Scroll.active_canvas == self._canvas:
            Scroll.active_canvas = None

    def create_compile_context(self, xml_node):
        return CompileContext(xml_node, self, self._container)

    def scroll_to(self, widget):
        widget_offset = (widget.winfo_y() - self._scroll.winfo_y()) / self._container.winfo_height()
        widget_relative_height = widget.winfo_height() / self._scroll.winfo_height()
        self.scroll_to_fraction(widget_offset - widget_relative_height)

    def scroll_to_fraction(self, fraction):
        (up_offset, down_offset) = self._scroll.get()
        if fraction < up_offset or fraction > down_offset:
            self._canvas.yview_moveto(fraction)

def create_scroll_frame(parent):
    frame = Frame(parent)
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(0, weight=1)
    return frame

def create_canvas(parent):
    canvas = Canvas(parent)
    canvas.grid(row=0, column=0, sticky='wens')
    return canvas

def create_scroll(parent, canvas):
    scroll = Scrollbar(parent, orient='vertical', command=canvas.yview)
    scroll.grid(row=0, column=1, sticky='ns')
    canvas.config(yscrollcommand=scroll.set, highlightthickness=0, bg='green')
    return scroll

def create_container(canvas):
    container = Frame(canvas)
    container.pack(fill='both', expand=True)
    container_window_sets = {
        'window': container,
        'anchor': 'nw'
    }
    container.win_id = canvas.create_window((0, 0), container_window_sets)
    return container
