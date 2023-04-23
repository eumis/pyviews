from unittest.mock import Mock, call, patch

from injectool import add_singleton
from pytest import fixture, mark, raises

from pyviews import pipes, setters
from pyviews.binding.binder import Binder, BindingContext
from pyviews.binding.expression import bind_setter_to_expression
from pyviews.binding.once import run_once
from pyviews.core.rendering import Node
from pyviews.core.xml import XmlAttr, XmlNode
from pyviews.pipes import apply_attribute, apply_attributes, call_set_attr, get_setter, render_children
from pyviews.rendering.context import RenderingContext
from pyviews.rendering.pipeline import render


@patch(pipes.__name__ + '.apply_attribute')
def test_apply_attributes(apply_attribute_mock):
    """should call apply_attribute for every attribute"""
    xml_node = Mock()
    xml_node.attrs = [Mock(), Mock()]
    node = Node(xml_node)
    context = RenderingContext()

    apply_attributes(node, context)

    calls = [call(node, attr) for attr in xml_node.attrs]
    assert apply_attribute_mock.call_args_list == calls


@fixture
def apply_attribute_fixture(request):
    setter_mock = Mock()
    get_setter_mock = Mock()
    get_setter_mock.side_effect = lambda _: setter_mock
    request.cls.setter_mock = setter_mock
    with patch(f'{pipes.__name__}.get_setter', get_setter_mock) as patched:
        binder = Binder()
        binder.add_rule('once', run_once)
        binder.add_rule('oneway', bind_setter_to_expression)
        add_singleton(Binder, binder)
        yield patched


@mark.usefixtures('container_fixture', 'apply_attribute_fixture')
class ApplyAttributeTests:
    """apply_attribute() tests"""

    setter_mock: Mock

    @mark.parametrize('xml_attr, key, value', [
        (XmlAttr('key', 'value'), 'key', 'value'),
        (XmlAttr('', 'value'), '', 'value'),
        (XmlAttr('one', '{1}'), 'one', 1),
        (XmlAttr('one', 'once:{1 + 1}'), 'one', 2)
    ]) # yapf: disable
    def test_imports_setter(self, xml_attr: XmlAttr, key, value):
        """ should call setter"""
        node = Node(Mock())

        apply_attribute(node, xml_attr)

        assert self.setter_mock.call_args == call(node, key, value)

    @mark.parametrize('xml_attr, key, value', [
        (XmlAttr('key', 'value'), 'key', 'value'),
        (XmlAttr('', 'value'), '', 'value'),
        (XmlAttr('one', '{1}'), 'one', 1),
        (XmlAttr('one', 'once:{1 + 1}'), 'one', 2)
    ]) # yapf: disable
    def test_uses_passed_setter(self, xml_attr: XmlAttr, key, value):
        """ should call setter"""
        node = Node(Mock())

        apply_attribute(node, xml_attr, self.setter_mock)

        assert self.setter_mock.call_args == call(node, key, value)

    @mark.parametrize('xml_attr, binding_type, expr_body', [
        (XmlAttr('key', '{1}'), 'oneway', '1'),
        (XmlAttr('one', 'oneway:{1 + 1}'), 'oneway', '1 + 1'),
        (XmlAttr('one', 'twoways:{vm.prop}'), 'twoways', 'vm.prop')
    ]) # yapf: disable
    def test_applies_binding(self, xml_attr, binding_type, expr_body):
        """should apply binding"""
        node = Node(Mock())
        binder = Mock()
        add_singleton(Binder, binder)
        binding_context = BindingContext({
            'node': node, 'xml_attr': xml_attr, 'setter': self.setter_mock, 'expression_body': expr_body
        })

        apply_attribute(node, xml_attr)
        assert binder.bind.call_args == call(binding_type, binding_context)


class GetSetterTests:
    """get_setter() tests"""

    @staticmethod
    @mark.parametrize('setter_path, expected_setter', [
        (None, call_set_attr),
        (setters.__name__ + '.import_global', setters.import_global)
    ]) # yapf: disable
    def test_returns_setter(setter_path, expected_setter):
        """should return appropriate setter"""
        actual_setter = get_setter(XmlAttr('', namespace = setter_path))

        assert actual_setter == expected_setter

    @staticmethod
    @mark.parametrize('namespace, name', [
        ('', ''),
        ('', 'attr_name'),
        ('tests.rendering.core_test.some_setter_not', 'attr_name')
    ]) # yapf: disable
    def test_raises(namespace, name):
        """should raise ImportError if namespace can''t be imported"""
        with raises(ImportError):
            xml_attr = XmlAttr(name, '', namespace)
            get_setter(xml_attr)


def test_call_set_attr():
    """should call node setter"""
    node = Node(Mock())
    node.set_attr = Mock()
    key, value = ('key', 'value')

    call_set_attr(node, key, value)

    assert node.set_attr.call_args == call(key, value)


@fixture
def render_children_fixture(request):
    render_mock = Mock()
    add_singleton(render, render_mock)

    xml_node = XmlNode('', '')
    node = Node(xml_node)

    request.cls.xml_node = xml_node
    request.cls.node = node
    request.cls.context = RenderingContext()
    request.cls.render = render_mock


@mark.usefixtures('container_fixture', 'render_children_fixture')
class RenderChildrenTests:
    """render_children pipe tests"""

    xml_node: XmlNode
    node: Node
    context: RenderingContext
    render: Mock

    @mark.parametrize('child_count', [1, 2, 5])
    def test_renders_children(self, child_count):
        self.xml_node.children.extend([Mock() for _ in range(child_count)])

        render_children(self.node, self.context, lambda x, n, c: (x, n, c))

        assert self.render.call_args_list == [
            call((xml_node, self.node, self.context)) for xml_node in self.xml_node.children
        ]

    @mark.parametrize('child_count', [1, 2, 5])
    def test_adds_children_to_node(self, child_count):
        self.xml_node.children.extend([Mock() for _ in range(child_count)])
        self.render.side_effect = lambda ctx: Node(ctx.xml_node)

        render_children(self.node, self.context, lambda x, *_: RenderingContext({'xml_node': x}))

        assert [child.xml_node for child in self.node.children] == self.xml_node.children
