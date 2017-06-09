from tkinter import Frame, Scrollbar, Canvas
from pyviews.view.base import CompileNode, NodeChild, get_handler
from pyviews.view.core import Container, apply_style
from pyviews.viewmodel.base import ViewModel
from pyviews.application import compile_view
from pyviews.common.values import STYLE

class For(Container):
    def __init__(self, parent_widget):
        Container.__init__(self, parent_widget)
        self._items = []
        self._render_children = None
        self._parent = None
        self._rendered_count = 0

    def get_xml_children(self):
        children = []
        for item in self._items[self._rendered_count:]:
            children += [NodeChild(xml_node, item) for xml_node in list(self._xml_node)]
        return children

    @property
    def items(self):
        return [vm.item for vm in self._items]

    @items.setter
    def items(self, val):
        val = list(val)
        new_count = len(val)
        old_count = len(self._items)
        if val:
            for index, item in enumerate(val):
                try:
                    self._items[index].item = item
                except IndexError:
                    self._items.append(ItemViewModel(item, self.view_model, index))
        else:
            self._items = []

        self._remove_items(new_count)
        self._render_items(old_count)

    def _remove_items(self, start_index):
        items = self._items[start_index:]
        childs_to_remove = [node for node in self._nodes if node.view_model in items]
        for child in childs_to_remove:
            child.destroy()
        self._nodes = [node for node in self._nodes if node not in childs_to_remove]
        self._items = self._items[:start_index]

    def _render_items(self, start_index):
        self._rendered_count = start_index
        self.render(self._render_children, self._parent)

    def clear(self):
        self._remove_items(self._items)
        self._rendered_count = 0

    def render(self, render_children, parent=None):
        self._render_children = render_children
        self._parent = parent
        if self._render_children:
            self._nodes += render_children(self)
            self._rendered_count = len(self._items)

class ItemViewModel(ViewModel):
    def __init__(self, item, parent, index):
        ViewModel.__init__(self)
        self.item = item
        self.parent = parent
        self.index = index

class View(Container):
    def __init__(self, parent_widget):
        super().__init__(parent_widget)
        self.path = None

    def render(self, render_children, parent=None):
        if self.path:
            compile_view(self.path, self)

class Scroll(CompileNode):
    def __init__(self, parent_widget):
        self._frame = create_scroll_frame(parent_widget)
        self._canvas = create_canvas(self._frame)
        self._scroll = create_scroll(self._frame, self._canvas)
        self._container = create_container(self._canvas)
        self._container.bind('<Configure>', self.config_container)
        self._canvas.bind('<Configure>', self.config_canvas)
        self.geometry = None
        super().__init__()

    def config_container(self, event):
        self._canvas.config(scrollregion=self._canvas.bbox("all"))

    def config_canvas(self, event):
        self._canvas.itemconfig(self._container.win_id, width=event.width)

    def get_widget(self):
        return self._frame

    def get_widget_master(self):
        return self._container

    def bind(self, event, command):
        self.get_widget_master().bind('<'+event+'>', get_handler(command))

    def has_attr(self, name):
        return True

    def set_attr(self, name, value):
        if name == STYLE:
            apply_style(self, value)
        elif hasattr(self, name):
            setattr(self, name, value)
        elif hasattr(self.get_widget_master(), name):
            setattr(self.get_widget_master(), name, value)

    def render(self, render_children, parent=None):
        self.geometry.apply(self.get_widget())
        super().render(render_children, parent)

    def config(self, key, value):
        self.get_widget_master().configure({key: value})
        if key == 'bg' or key == 'background':
            self._canvas.config({key: value})

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
    return canvas

def create_container(canvas):
    container = Frame(canvas)
    container.pack(fill='both', expand=True)
    container_window_sets = {
        'window': container,
        'anchor': 'nw'
    }
    container.win_id = canvas.create_window((0, 0), container_window_sets)
    return container
