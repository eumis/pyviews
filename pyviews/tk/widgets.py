from tkinter import Tk, Widget, Canvas, Frame, Scrollbar, StringVar
from collections import namedtuple
from pyviews.core.ioc import inject
from pyviews.core.xml import XmlNode
from pyviews.core.compilation import ExpressionVars
from pyviews.core.parsing import Node, NodeArgs
from pyviews.core.observable import Observable
from pyviews.tk.views import get_view_root

class WidgetArgs(NodeArgs):
    def __init__(self, xml_node, parent_node=None, widget_master=None):
        super().__init__(xml_node, parent_node)
        self['master'] = widget_master

    def get_args(self, inst_type=None):
        if issubclass(inst_type, Widget):
            return namedtuple('Args', ['args', 'kwargs'])([self['master']], {})
        return super().get_args(inst_type)

class WidgetNode(Node, Observable):
    def __init__(self, widget, xml_node: XmlNode, parent_globals: ExpressionVars = None):
        Observable.__init__(self)
        Node.__init__(self, xml_node, parent_globals)
        self.widget = widget
        self._geometry = None

    @property
    def geometry(self):
        return self._geometry

    @geometry.setter
    def geometry(self, value):
        self._geometry = value
        if value is not None:
            value.apply(self.widget)

    @property
    def view_model(self):
        try:
            return self.globals['vm']
        except KeyError:
            return None

    @view_model.setter
    def view_model(self, value):
        self.globals['vm'] = value

    def get_node_args(self, xml_node: XmlNode):
        return WidgetArgs(xml_node, self, self.widget)

    def destroy(self):
        super().destroy()
        self.widget.destroy()

    def bind(self, event, command):
        self.widget.bind('<'+event+'>', command)

    def set_attr(self, key, value):
        if key == 'style':
            self._apply_style(value)
        elif hasattr(self, key):
            setattr(self, key, value)
        elif hasattr(self.widget, key):
            setattr(self.widget, key, value)
        else:
            self.widget.configure(**{key:value})

    def _apply_style(self, styles):
        keys = styles.split(',') if isinstance(styles, str) else styles
        for key in [key for key in keys if key]:
            for item in self.globals[key]:
                item.apply(self)

class EntryWidget(WidgetNode):
    def __init__(self, widget, xml_node: XmlNode, parent_globals: ExpressionVars = None):
        super().__init__(widget, xml_node, parent_globals)
        self._text_var = StringVar()
        self._text_var.trace_add('write', self._write_callback)
        self._text_value = self._text_var.get()
        widget.config(textvariable=self._text_var)

    def _write_callback(self, *args):
        old_value = self._text_value
        self._text_value = self._text_var.get()
        self._notify('text', self._text_value, old_value)

    def set_attr(self, key, value):
        if key == 'text':
            self._text_var.set(str(value))
        else:
            super().set_attr(key, value)

class Root(WidgetNode):
    def __init__(self, xml_node: XmlNode, parent_globals: ExpressionVars = None):
        super().__init__(Tk(), xml_node, parent_globals)

    @property
    def state(self):
        return self.widget.state()

    @state.setter
    def state(self, state):
        self.widget.state(state)

class Container(Node):
    def __init__(self, master, xml_node: XmlNode, parent_globals: ExpressionVars = None):
        super().__init__(xml_node, parent_globals)
        self.master = master

    @property
    def view_model(self):
        try:
            return self.globals['vm']
        except KeyError:
            return None

    @view_model.setter
    def view_model(self, value):
        self.globals['vm'] = value

    def set_attr(self, key, value):
        setattr(self, key, value)

    def get_node_args(self, xml_node):
        return WidgetArgs(xml_node, self, self.master)

class View(Container):
    def __init__(self, master, xml_node: XmlNode, parent_globals: ExpressionVars = None):
        super().__init__(master, xml_node, parent_globals)
        self._name = None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if self._name == value:
            return
        self._name = value
        self.parse_children()

    @inject('parse')
    def parse_children(self, parse=None):
        self.destroy_children()
        try:
            root_xml = get_view_root(self.name)
            self._child_nodes = [parse(root_xml, self.get_node_args(root_xml))]
        except FileNotFoundError:
            self._child_nodes = []

class For(Container):
    def __init__(self, master, xml_node: XmlNode, parent_globals: ExpressionVars = None):
        super().__init__(master, xml_node, parent_globals)
        self._items = []
        self._rendered = False

    @property
    def items(self):
        return self._items

    @items.setter
    def items(self, val):
        self._items = val
        if self._rendered:
            self._destroy_overflow()
            self._update_existing()
            self._create_not_existing()

    def _destroy_overflow(self):
        try:
            items_count = len(self._items)
            children = self._child_nodes[items_count:]
            for child in children:
                child.destroy()
            self._child_nodes = self._child_nodes[:items_count]
        except IndexError:
            pass

    def _update_existing(self):
        try:
            for index, item in enumerate(self._items):
                self._child_nodes[index].globals['item'] = item
                self._child_nodes[index].globals['index'] = index
        except IndexError:
            pass

    def _create_not_existing(self):
        start = len(self._child_nodes)
        end = len(self._items)
        self._create_children([(i, self._items[i]) for i in range(start, end)])

    @inject('parse')
    def _create_children(self, items, parse=None):
        for index, item in items:
            for xml_node in self.xml_node.get_children():
                args = self.get_node_args(xml_node, index)
                self._child_nodes.append(parse(xml_node, args))

    def parse_children(self):
        self._rendered = True
        self.destroy_children()
        self._create_children(enumerate(self._items))

    def get_node_args(self, xml_node: XmlNode, index=None):
        args = super().get_node_args(xml_node)
        args_globals = ExpressionVars(args['parent_globals'])
        args_globals['index'] = index
        if index is not None:
            args_globals['item'] = self._items[index]
        args['parent_globals'] = args_globals
        return args

class Scroll(Node):
    def __init__(self, master, xml_node: XmlNode, parent_globals: ExpressionVars = None):
        super().__init__(xml_node, parent_globals)
        self._frame = self._create_scroll_frame(master)
        self._canvas = self._create_canvas(self._frame)
        self._scroll = self._create_scroll(self._frame, self._canvas)
        self._container = self._create_container(self._canvas)
        self._container.bind('<Configure>', lambda event: self._config_container())
        self._canvas.bind('<Configure>', self._config_canvas)
        self._canvas.bind_all('<MouseWheel>', self._on_mouse_scroll)
        self._canvas.bind('<Enter>', lambda event: self._set_canvas_active())
        self._canvas.bind('<Leave>', lambda event: self._set_canvas_inactive())
        self._geometry = None

    def _create_scroll_frame(self, master):
        frame = Frame(master)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        return frame


    def _create_canvas(self, master):
        canvas = Canvas(master)
        canvas.grid(row=0, column=0, sticky='wens')
        return canvas

    def _create_scroll(self, master, canvas):
        scroll = Scrollbar(master, orient='vertical', command=canvas.yview)
        scroll.grid(row=0, column=1, sticky='ns')
        canvas.config(yscrollcommand=scroll.set, highlightthickness=0, bg='green')
        return scroll

    def _create_container(self, canvas):
        container = Frame(canvas)
        container.pack(fill='both', expand=True)
        container_window_sets = {
            'window': container,
            'anchor': 'nw'
        }
        container.win_id = canvas.create_window((0, 0), container_window_sets)
        return container

    def _config_container(self):
        self._canvas.config(scrollregion=self._canvas.bbox("all"))

    def _config_canvas(self, event):
        self._canvas.itemconfig(self._container.win_id, width=event.width)

    def _on_mouse_scroll(self, event):
        if Scroll.active_canvas and self._is_active():
            Scroll.active_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def _is_active(self):
        (up_offset, down_offset) = self._scroll.get()
        return not (up_offset == 0.0 and down_offset == 1.0)

    def _set_canvas_active(self):
        Scroll.active_canvas = self._canvas

    def _set_canvas_inactive(self):
        if Scroll.active_canvas == self._canvas:
            Scroll.active_canvas = None

    @property
    def geometry(self):
        return self._geometry

    @geometry.setter
    def geometry(self, value):
        self._geometry = value
        if value is not None:
            value.apply(self._frame)

    @property
    def view_model(self):
        try:
            return self.globals['vm']
        except KeyError:
            return None

    @view_model.setter
    def view_model(self, value):
        self.globals['vm'] = value

    def set_attr(self, name, value):
        if name == 'style':
            self._apply_style(value)
        elif hasattr(self, name):
            setattr(self, name, value)
        elif hasattr(self._container, name):
            setattr(self._container, name, value)
        else:
            self._container.configure(**{name: value})
            if name == 'bg' or name == 'background':
                self._canvas.config(**{name: value})

    def _apply_style(self, styles):
        keys = styles.split(',') if isinstance(styles, str) else styles
        for key in [key for key in keys if key]:
            for item in self.globals[key]:
                item.apply(self)

    def bind(self, event, handler):
        self._container.bind('<'+event+'>', handler)
        if 'Button-' in event:
            self._canvas.bind('<'+event+'>', handler)

    def get_node_args(self, xml_node):
        return WidgetArgs(xml_node, self, self._container)

    def destroy(self):
        super().destroy()
        self._frame.destroy()
