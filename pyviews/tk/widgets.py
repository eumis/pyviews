from tkinter import Tk, Widget, Canvas, Frame, Scrollbar, StringVar, Entry
from collections import namedtuple
from pyviews.core.ioc import inject
from pyviews.core.xml import XmlNode
from pyviews.core.compilation import ExpressionVars
from pyviews.core.binding import Bindable, BindableVariable
from pyviews.core.parsing import Node, NodeArgs
from pyviews.tk.views import get_view_root

class WidgetArgs(NodeArgs):
    def __init__(self, xml_node, parent_node=None, widget_master=None):
        super().__init__(xml_node, parent_node)
        self['master'] = widget_master

    def get_args(self, inst_type=None):
        if issubclass(inst_type, Widget):
            return namedtuple('Args', ['args', 'kwargs'])([self['master']], {})
        return super().get_args(inst_type)

class TextBindableVariable(BindableVariable):
    def __init__(self, tk_var):
        self._tk_var = tk_var
        self._tk_var.trace_add('write', self._write_callback)
        self._callback = None

    def _write_callback(self, *args):
        if self._callback is not None:
            value = self.get_value()
            if value is not None:
                self._callback(value, None)

    def get_value(self):
        try:
            return int(self._tk_var.get())
        except:
            return None

    def set_value(self, value):
        self._tk_var.set(value)

    def observe(self, callback):
        self._callback = callback

    def release(self):
        self._callback = None

class WidgetNode(Node, Bindable):
    def __init__(self, widget, xml_node: XmlNode, parent_globals: ExpressionVars = None):
        super().__init__(xml_node, parent_globals)
        self.widget = widget
        self._geometry = None
        self._text_var = None

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

    def get_variable(self, key, modifier=None):
        if key == 'text' and isinstance(self.widget, Entry):
            if self._text_var is not None:
                return self._text_var
            var = StringVar()
            self._text_var = TextBindableVariable(var)
            self.widget.config(textvariable=var)
            return self._text_var

    def get_node_args(self, xml_node: XmlNode):
        return WidgetArgs(xml_node, self, self.widget)

    def destroy(self):
        super().destroy()
        self.widget.destroy()

    def bind(self, event, command):
        self.widget.bind('<'+event+'>', command)

    def set_attr(self, key, value):
        if hasattr(self, key):
            setattr(self, key, value)
        elif hasattr(self.widget, key):
            setattr(self.widget, key, value)
        else:
            self.widget.configure(**{key:value})

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
        root_xml = get_view_root(self.name)
        self._child_nodes = [parse(root_xml, self.get_node_args(root_xml))]

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
            self.parse_children()

    @inject('parse')
    def parse_children(self, parse=None):
        self._rendered = True
        self.destroy_children()
        for index, item in enumerate(self._items):
            for xml_node in self.xml_node.get_children():
                args = self.get_node_args(xml_node, index)
                self._child_nodes.append(parse(xml_node, args))

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
        if hasattr(self, name):
            setattr(self, name, value)
        elif hasattr(self._container, name):
            setattr(self._container, name, value)
        else:
            self._container.configure(**{name: value})
            if name == 'bg' or name == 'background':
                self._canvas.config(**{name: value})

    def bind(self, event, handler):
        self._container.bind('<'+event+'>', handler)
        if 'Button-' in event:
            self._canvas.bind('<'+event+'>', handler)

    def get_node_args(self, xml_node):
        return WidgetArgs(xml_node, self, self._container)
