from unittest.mock import Mock, call

from pyviews.core import Node, InheritedDict
from pyviews.presenter import Presenter, PresenterNode, add_presenter_to_globals, call_on_rendered, add_reference
from pyviews.rendering import RenderingContext


class TestPresenter(Presenter):
    @property
    def one(self):
        return self._references['one']


class PresenterTests:
    @staticmethod
    def test_add_reference():
        """should add reference"""
        presenter = TestPresenter()
        node = Mock()

        presenter.add_reference('one', node)

        assert presenter.one == node


def test_add_presenter_to_globals():
    """should add presenter to node globals"""
    presenter = Mock()
    node = PresenterNode(presenter, Mock())

    add_presenter_to_globals(node, RenderingContext())

    assert node.node_globals['presenter'] == presenter


def test_call_on_rendered():
    """should call on_rendered method of presenter"""
    presenter = Mock()
    node = PresenterNode(presenter, Mock())

    call_on_rendered(node, RenderingContext())

    assert presenter.on_rendered.called


def test_add_reference():
    """should add reference to node to presenter by passed key"""
    presenter = Mock(add_reference=Mock())
    node = Node(Mock(), node_globals=InheritedDict({'presenter': presenter}))

    add_reference(node, '', 'key')

    assert presenter.add_reference.call_args == call('key', node)
