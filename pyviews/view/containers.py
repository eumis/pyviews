from tkinter import Frame, Scrollbar, Canvas
from pyviews.view.base import CompileNode
from pyviews.view.core import Container, apply_style
from pyviews.common.settings import STYLE
from pyviews.common.reflection import get_handler
from pyviews.common.compiling import CompileContext
from pyviews.common.parsing import parse_xml

class For(Container):
    def __init__(self, parent_widget):
        Container.__init__(self, parent_widget)
        self._items = []
        self._render_children = None
        self._parent = None
        self._rendered_count = 0

    @property
    def items(self):
        return self._items

    @items.setter
    def items(self, val):
        val = list(val) if val is not None else []
        self._items = self._items[len(val):]
        for index, item in enumerate(val):
            try:
                if self._items[index] != item:
                    self._items[index] = item
            except IndexError:
                self._items.append(item)

    def _remove_items(self, start_index):
        items = self._items[start_index:]
        childs_to_remove = [node for node in self._nodes if node.view_model in items]
        for child in childs_to_remove:
            child.destroy()
        self._nodes = [node for node in self._nodes if node not in childs_to_remove]
        self._items = self._items[:start_index]

    def _render_items(self, start_index):
        self._rendered_count = start_index
        self.render()

    def clear(self):
        self._remove_items(self._items)
        self._rendered_count = 0

    def render(self):
        if len(self._items) < self._rendered_count:
            self._remove_items(len(self._items))

        for index, item in enumerate(self._items[self._rendered_count:]):
            for xml_node in list(self.xml_node):
                context = self.create_compile_context(xml_node)
                context.globals['item'] = item
                context.globals['index'] = index
                self._nodes += self.compile_xml(context)
        self._rendered_count = len(self._items)

    def create_compile_context(self, xml_node):
        return CompileContext(xml_node, self)

class View(Container):
    def __init__(self, master):
        super().__init__(master)
        self._path = None

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        if value == self._path:
            return
        self._path = value
        if self._path:
            self._clear_xml_node()
            self.xml_node.append(parse_xml(self._path))
        self.render()

    def _clear_xml_node(self):
        # nodes = [node for node in self.xml_node]
        for node in list(self.xml_node):
            self.xml_node.remove(node)

    def render(self):
        if self._path:
            super().render()
        else:
            super().clear()

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
        self.render()

    def render(self):
        if self._true:
            super().render()
        else:
            super().clear()

class Scroll(CompileNode):
    def __init__(self, parent_widget):
        self._frame = create_scroll_frame(parent_widget)
        self._canvas = create_canvas(self._frame)
        self._scroll = create_scroll(self._frame, self._canvas)
        self._container = create_container(self._canvas)
        self._container.bind('<Configure>', lambda event: self.config_container())
        self._canvas.bind('<Configure>', self.config_canvas)
        self._canvas.bind_all('<MouseWheel>', self.on_mouse_scroll)
        self._canvas.bind('<Enter>', lambda event: self.set_canvas_active())
        self._canvas.bind('<Leave>', lambda event: self.set_canvas_inactive())
        self.geometry = None
        super().__init__()

    def config_container(self):
        self._canvas.config(scrollregion=self._canvas.bbox("all"))

    def config_canvas(self, event):
        self._canvas.itemconfig(self._container.win_id, width=event.width)

    def bind(self, event, command):
        handler = get_handler(command)
        self._container.bind('<'+event+'>', handler)
        if 'Button-' in event:
            self._canvas.bind('<'+event+'>', handler)

    def has_attr(self, name):
        return True

    def set_attr(self, name, value):
        if name == STYLE:
            apply_style(self, value)
        elif hasattr(self, name):
            setattr(self, name, value)
        elif hasattr(self._container, name):
            setattr(self._container, name, value)

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

    def render(self):
        self.geometry.apply(self._frame)
        super().render()

    def create_compile_context(self, xml_node):
        return CompileContext(xml_node, self, self._container)

    def config(self, key, value):
        self._container.configure({key: value})
        if key == 'bg' or key == 'background':
            self._canvas.config({key: value})

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
