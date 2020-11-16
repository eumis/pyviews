"""Contains methods for node setups creation"""
from typing import Any

from pyviews.core import Node, XmlNode
from pyviews.core.observable import InheritedDict, Observable
from pyviews.pipes import render_children, apply_attributes
from pyviews.rendering import RenderingPipeline, render, RenderingContext, get_child_context
from pyviews.rendering.views import render_view


class Container(Node):
    """Used to combine some xml elements"""


def get_container_pipeline() -> RenderingPipeline:
    """Returns setup for container"""
    return RenderingPipeline(pipes=[
        apply_attributes,
        render_container_children
    ], name='container pipeline')


def render_container_children(node, context: RenderingContext):
    """Renders container children"""
    render_children(node, context, get_child_context)


class View(Container, Observable):
    """Loads xml from another file"""

    def __init__(self, xml_node: XmlNode, node_globals: InheritedDict = None):
        Observable.__init__(self)
        Container.__init__(self, xml_node, node_globals=node_globals)
        self._name = None

    @property
    def name(self) -> str:
        """Returns view name"""
        return self._name

    @name.setter
    def name(self, value: str):
        old_name = self._name
        self._name = value
        self._notify('name', value, old_name)


def get_view_pipeline() -> RenderingPipeline:
    """Returns setup for container"""
    return RenderingPipeline(pipes=[
        apply_attributes,
        render_view_content,
        rerender_on_view_change
    ], name='view pipeline')


def render_view_content(node: View, context: RenderingContext):
    """Finds view by name attribute and renders it as view node child"""
    if node.name:
        child_context = get_child_context(node.xml_node, node, context)
        content = render_view(node.name, child_context)
        node.add_child(content)


def rerender_on_view_change(node: View, context: RenderingContext):
    """Subscribes to name change and renders new view"""
    node.observe('name', lambda _, __: _rerender_view(node, context))


def _rerender_view(node: View, context: RenderingContext):
    node.destroy_children()
    render_view_content(node, context)


class For(Container, Observable):
    """Renders children for every item in items collection"""

    def __init__(self, xml_node: XmlNode, node_globals: InheritedDict = None):
        Observable.__init__(self)
        Container.__init__(self, xml_node, node_globals=node_globals)
        self._items = []

    @property
    def items(self):
        """Returns items"""
        return self._items

    @items.setter
    def items(self, value):
        old_items = self._items
        self._items = value
        self._notify('items', value, old_items)


def get_for_pipeline() -> RenderingPipeline:
    """Returns setup for For node"""
    return RenderingPipeline(pipes=[
        apply_attributes,
        render_for_items,
        rerender_on_items_change
    ], name='for pipeline')


def render_for_items(node: For, context: RenderingContext):
    """Renders For children"""
    _render_for_children(node, node.items, context)


def _render_for_children(node: For, items: list, context: RenderingContext, index_shift=0):
    item_xml_nodes = node.xml_node.children
    for index, item in enumerate(items):
        for xml_node in item_xml_nodes:
            child_context = _get_for_child_args(xml_node, index + index_shift, item, node, context)
            child = render(child_context)
            node.add_child(child)


def _get_for_child_args(xml_node: XmlNode, index: int, item: Any,
                        parent_node: For, context: RenderingContext):
    child_context = get_child_context(xml_node, parent_node, context)
    child_globals = child_context.node_globals
    child_globals['index'] = index
    child_globals['item'] = item
    return child_context


def rerender_on_items_change(node: For, context: RenderingContext):
    """Subscribes to items change and updates children"""
    node.observe('items', lambda _, __: _on_items_changed(node, context))


def _on_items_changed(node: For, context: RenderingContext):
    _destroy_overflow(node)
    _update_existing(node)
    _create_not_existing(node, context)


def _destroy_overflow(node: For):
    try:
        items_count = len(node.items)
        children_count = len(node.xml_node.children) * items_count
        overflow = node.children[children_count:]
        for child in overflow:
            child.destroy()
        node._children = node.children[:children_count]
    except IndexError:
        pass


def _update_existing(node: For):
    item_children_count = len(node.xml_node.children)
    try:
        for index, item in enumerate(node.items):
            start = index * item_children_count
            end = (index + 1) * item_children_count
            for child_index in range(start, end):
                globs = node.children[child_index].node_globals
                globs['item'] = item
                globs['index'] = index
    except IndexError:
        pass


def _create_not_existing(node: For, context: RenderingContext):
    item_children_count = len(node.xml_node.children)
    start = int(len(node.children) / item_children_count)
    end = len(node.items)
    items = [node.items[i] for i in range(start, end)]
    _render_for_children(node, items, context, start)


class If(Container, Observable):
    """Renders children if condition is True"""

    def __init__(self, xml_node: XmlNode, node_globals: InheritedDict = None):
        Observable.__init__(self)
        Container.__init__(self, xml_node, node_globals=node_globals)
        self._condition = False

    @property
    def condition(self):
        """Returns condition"""
        return self._condition

    @condition.setter
    def condition(self, value):
        old_condition = self._condition
        self._condition = value
        self._notify('condition', value, old_condition)


def get_if_pipeline() -> RenderingPipeline:
    """Returns setup for For node"""
    return RenderingPipeline(pipes=[
        apply_attributes,
        render_if,
        rerender_on_condition_change
    ], name='if pipeline')


def render_if(node: If, context: RenderingContext):
    """Renders children nodes if condition is true"""
    if node.condition:
        render_children(node, context, get_child_context)


def rerender_on_condition_change(node: If, context: RenderingContext):
    """Rerenders if on condition change"""
    node.observe('condition', lambda _, __: _on_condition_change(node, context))


def _on_condition_change(node: If, context: RenderingContext):
    node.destroy_children()
    render_if(node, context)
