from tkinter import Tk, Widget, StringVar
from pyviews.core.xml import XmlNode
from pyviews.core.compilation import IhertiedDict
from pyviews.core.node import Node, NodeArgs
from pyviews.core.observable import Observable

class WidgetArgs(NodeArgs):
    def __init__(self, xml_node, parent_node=None, widget_master=None):
        super().__init__(xml_node, parent_node)
        self['master'] = widget_master

    def get_args(self, inst_type=None):
        if issubclass(inst_type, Widget):
            return NodeArgs.args_tuple([self['master']], {})
        return super().get_args(inst_type)

class WidgetNode(Node, Observable):
    def __init__(self, widget, xml_node: XmlNode, parent_globals: IhertiedDict = None):
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

    def bind_all(self, event, command):
        self.widget.bind_all('<'+event+'>', command, '+')

    def set_attr(self, key, value):
        if hasattr(self, key):
            setattr(self, key, value)
        elif hasattr(self.widget, key):
            setattr(self.widget, key, value)
        else:
            self.widget.configure(**{key:value})

class EntryWidget(WidgetNode):
    def __init__(self, widget, xml_node: XmlNode, parent_globals: IhertiedDict = None):
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
    def __init__(self, xml_node: XmlNode, parent_globals: IhertiedDict = None):
        super().__init__(Tk(), xml_node, parent_globals)
        self._icon = None

    @property
    def state(self):
        return self.widget.state()

    @state.setter
    def state(self, state):
        self.widget.state(state)

    @property
    def icon(self):
        return self._icon

    @icon.setter
    def icon(self, value):
        self._icon = value
        self.widget.iconbitmap(default=value)
