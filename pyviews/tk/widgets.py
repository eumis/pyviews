'''Tkinter widgets nodes'''

from tkinter import Tk, Widget, StringVar
from pyviews.core.ioc import inject
from pyviews.core.xml import XmlNode
from pyviews.core.node import Node, NodeArgs
from pyviews.core.observable import Observable

class WidgetArgs(NodeArgs):
    '''NodeArgs for WidgetNode'''
    def __init__(self, xml_node, parent_node=None, widget_master=None):
        super().__init__(xml_node, parent_node)
        self['master'] = widget_master

    def get_args(self, inst_type=None):
        if issubclass(inst_type, Widget):
            return NodeArgs.args_tuple([self['master']], {})
        return super().get_args(inst_type)

class WidgetNode(Node, Observable):
    '''Wrapper under tkinter widget'''
    def __init__(self, widget, xml_node: XmlNode, parent_context=None):
        Observable.__init__(self)
        Node.__init__(self, xml_node, parent_context)
        self.widget = widget
        self._geometry = None
        self._style = ''

    @property
    def geometry(self):
        '''Geometry'''
        return self._geometry

    @geometry.setter
    def geometry(self, value):
        self._geometry = value
        if value is not None:
            value.apply(self.widget)

    @property
    def style(self):
        '''Widget style'''
        return self._style

    @style.setter
    @inject('apply_styles')
    def style(self, value, apply_styles=None):
        self._style = value
        apply_styles(self, value)

    def get_node_args(self, xml_node: XmlNode):
        return WidgetArgs(xml_node, self, self.widget)

    def destroy(self):
        super().destroy()
        self.widget.destroy()

    def bind(self, event, command):
        '''Calls widget's bind'''
        self.widget.bind('<'+event+'>', command)

    def bind_all(self, event, command):
        '''Calls widget's bind_all'''
        self.widget.bind_all('<'+event+'>', command, '+')

    def set_attr(self, key, value):
        '''Applies passed attribute'''
        if hasattr(self, key):
            setattr(self, key, value)
        elif hasattr(self.widget, key):
            setattr(self.widget, key, value)
        else:
            self.widget.configure(**{key:value})

class EntryWidget(WidgetNode):
    '''Wrapper under Entry widget'''
    def __init__(self, widget, xml_node: XmlNode, parent_context=None):
        super().__init__(widget, xml_node, parent_context)
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
    '''Wrapper under tkinter Root'''
    def __init__(self, xml_node: XmlNode):
        super().__init__(Tk(), xml_node)
        self._icon = None

    @property
    def state(self):
        '''Widget state'''
        return self.widget.state()

    @state.setter
    def state(self, state):
        self.widget.state(state)

    @property
    def icon(self):
        '''Icon path'''
        return self._icon

    @icon.setter
    def icon(self, value):
        self._icon = value
        self.widget.iconbitmap(default=value)
