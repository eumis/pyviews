"""Presenter"""

from abc import ABC
from typing import Dict, Union

from pyviews.core import XmlNode, InheritedDict, Node
from pyviews.core.rendering import InstanceNode
from pyviews.pipes import apply_attributes, render_children
from pyviews.rendering import RenderingPipeline, RenderingContext, get_child_context


class Presenter(ABC):
    """Base class for presenters"""

    def __init__(self):
        self._references: Dict[str, Union[Node, InstanceNode]] = {}

    def add_reference(self, key: str, node: Node):
        """adds reference to node"""
        self._references[key] = node

    def on_rendered(self):
        """called when child nodes are rendered"""


class PresenterNode(InstanceNode):
    """Presenter node"""

    def __init__(self, instance: 'Presenter', xml_node: XmlNode,
                 node_globals: InheritedDict = None):
        super().__init__(instance, xml_node, node_globals=node_globals)

    @property
    def instance(self) -> Presenter:
        return self._instance

    @instance.setter
    def instance(self, value: Presenter):
        self._instance = value


def get_presenter_pipeline() -> RenderingPipeline:
    """Returns setup for PresenterNode"""
    return RenderingPipeline(pipes=[
        apply_attributes,
        add_presenter_to_globals,
        render_presenter_children,
        call_on_rendered
    ], create_node=create_presenter_node, name='presenter pipeline')


def add_presenter_to_globals(node: PresenterNode, _: RenderingContext):
    """Adds presenter instance to globals with 'presenter' key"""
    node.node_globals['presenter'] = node.instance


def call_on_rendered(node: PresenterNode, _: RenderingContext):
    """Calls on_rendered method of presenter"""
    node.instance.on_rendered()


def render_presenter_children(node, context: RenderingContext):
    """Renders container children"""
    render_children(node, context, get_child_context)


def create_presenter_node(context: RenderingContext) -> PresenterNode:
    """Create presenter node"""
    return PresenterNode(None, context.xml_node, node_globals=context.node_globals)


def add_reference(node: Node, _: str, value: str):
    """Adds node reference to presenter"""
    presenter: Presenter = node.node_globals['presenter']
    presenter.add_reference(value, node)
