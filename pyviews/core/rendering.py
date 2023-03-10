"""Core classes for creation from xml nodes"""

from functools import partial
from typing import Any, Callable, List, Optional, Set, Union

from pyviews.core.bindable import BindableDict
from pyviews.core.binding import Binding
from pyviews.core.error import PyViewsError, ViewInfo
from pyviews.core.xml import XmlNode


class NodeGlobals(BindableDict):

    def __init__(self, parent: Optional[Union[dict, 'BindableDict']] = None):
        super().__init__(parent)
        self._own_keys: Set[str] = set()
        self._parent: Optional[BindableDict] = None
        if isinstance(parent, BindableDict):
            self._use_parent(parent)

    def _use_parent(self, parent: BindableDict):
        """Subscribe to parent"""
        self._parent = parent
        self._parent.observe_all(self._parent_changed)

    def _parent_changed(self, key: Any, value: Any, _: Any):
        if key in self._own_keys:
            return
        super().__setitem__(key, value)

    def __delitem__(self, key: str):
        if self._parent and key in self._parent:
            super().__setitem__(key, self._parent[key])
            self._own_keys.remove(key)
        else:
            super().__delitem__(key)
            self._own_keys.remove(key)

    def __setitem__(self, key: Any, value: Any):
        self._own_keys.add(key)
        super().__setitem__(key, value)

    def pop(self, key: Any, default: Any = None) -> Any:
        if self._parent and key in self._parent:
            value = self[key] if key in self._own_keys else default
            super().__setitem__(key, self._parent[key])
        else:
            value = super().pop(key, default)
        if key in self._own_keys:
            self._own_keys.remove(key)
        return value


class Node:
    """Represents node with properties and bindings created from xml node"""

    def __init__(self, xml_node: XmlNode, node_globals: Optional[NodeGlobals] = None):
        self._children: List[Node] = []
        self._bindings: List[Binding] = []
        self._xml_node: XmlNode = xml_node
        self._globals: NodeGlobals = NodeGlobals() if node_globals is None else node_globals
        self._globals['node'] = self
        self.set_attr: Callable[[str, Any], None] = partial(setattr, self)
        self.on_destroy: Callable[[Node], None] = lambda _: None

    @property
    def xml_node(self) -> XmlNode:
        """Returns xml node"""
        return self._xml_node

    @property
    def node_globals(self) -> NodeGlobals:
        """Values used with expression executing"""
        return self._globals

    @property
    def children(self) -> List:
        """Returns child nodes"""
        return self._children

    def add_binding(self, binding: Binding):
        """Stores binding"""
        self._bindings.append(binding)

    def add_child(self, child: 'Node'):
        """Adds rendered child"""
        self._children.append(child)

    def add_children(self, children: List['Node']):
        """Adds list of rendered children"""
        self._children = self._children + children

    def destroy(self):
        """Destroys node"""
        self.destroy_children()
        self.destroy_bindings()
        self.on_destroy(self)

    def destroy_children(self):
        """Destroys and removes all bindings"""
        for child in self._children:
            child.destroy()
        self._children = []

    def destroy_bindings(self):
        """Destroys and removes all bindings"""
        for binding in self._bindings:
            binding.destroy()
        self._bindings = []


class InstanceNode(Node):
    """Represents Node that wraps instance created from xml node"""

    def __init__(self, instance: Any, xml_node: XmlNode, node_globals: Optional[NodeGlobals] = None):
        super().__init__(xml_node, node_globals)
        self._instance = instance
        self.set_attr = partial(_instance_attr_setter, self)

    @property
    def instance(self):
        """Returns rendered instance"""
        return self._instance


def _instance_attr_setter(node: InstanceNode, key, value):
    ent = node if hasattr(node, key) else node.instance
    setattr(ent, key, value)


Setter = Callable[[Node, str, Any], None]


class RenderingError(PyViewsError):
    """Error for rendering"""

    def __init__(self, message: str = '', view_info: Optional[ViewInfo] = None):
        super().__init__(message = message, view_info = view_info)


class RenderingContext(dict):
    """Used as rendering arguments container, passed to rendering step"""

    @property
    def node_globals(self) -> NodeGlobals:
        """Node globals"""
        return self.get('node_globals', None)

    @node_globals.setter
    def node_globals(self, value: NodeGlobals):
        self['node_globals'] = value

    @property
    def parent_node(self) -> Node:
        """Parent node"""
        return self.get('parent_node', None)

    @parent_node.setter
    def parent_node(self, value: Node):
        self['parent_node'] = value

    @property
    def xml_node(self) -> XmlNode:
        """xml node"""
        return self.get('xml_node', None)

    @xml_node.setter
    def xml_node(self, value: XmlNode):
        self['xml_node'] = value
