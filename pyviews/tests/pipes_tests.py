from unittest.mock import Mock, patch, call

from injectool import add_singleton, add_function_resolver
from pytest import fixture, mark

from pyviews.binding import Binder, OnceRule, OnewayRule, BindingContext
from pyviews.compilation import CompiledExpression
from pyviews.core import Expression, XmlAttr, Node
from pyviews import pipes
from pyviews.pipes import apply_attribute, apply_attributes
from pyviews.rendering2.common import RenderingContext


@fixture
def apply_attribute_fixture(request):
    setter_mock = Mock()
    get_setter_mock = Mock()
    get_setter_mock.side_effect = lambda attr: setter_mock
    request.cls.setter_mock = setter_mock
    with patch(f'{pipes.__name__}.get_setter', get_setter_mock) as patched:
        binder = Binder()
        binder.add_rule('once', OnceRule())
        binder.add_rule('oneway', OnewayRule())
        add_singleton(Binder, binder)
        add_function_resolver(Expression, lambda c, p=None: CompiledExpression(p))
        yield patched


@mark.usefixtures('container_fixture', 'apply_attribute_fixture')
class ApplyAttributeTests:
    """apply_attribute() tests"""

    @mark.parametrize('xml_attr, key, value', [
        (XmlAttr('key', 'value'), 'key', 'value'),
        (XmlAttr('', 'value'), '', 'value'),
        (XmlAttr('one', '{1}'), 'one', 1),
        (XmlAttr('one', 'once:{1 + 1}'), 'one', 2)
    ])
    def test_calls_setter(self, xml_attr: XmlAttr, key, value):
        """ should call setter"""
        node = Node(Mock())

        apply_attribute(node, xml_attr)

        assert self.setter_mock.call_args == call(node, key, value)

    @mark.parametrize('xml_attr, binding_type, expr_body', [
        (XmlAttr('key', '{1}'), 'oneway', '1'),
        (XmlAttr('one', 'oneway:{1 + 1}'), 'oneway', '1 + 1'),
        (XmlAttr('one', 'twoways:{vm.prop}'), 'twoways', 'vm.prop')
    ])
    def test_applies_binding(self, xml_attr, binding_type, expr_body):
        """should apply binding"""
        node = Node(Mock())
        binder = Mock()
        add_singleton(Binder, binder)
        binding_context = BindingContext({
            'node': node,
            'xml_attr': xml_attr,
            'modifier': self.setter_mock,
            'expression_body': expr_body
        })

        apply_attribute(node, xml_attr)
        assert binder.apply.call_args == call(binding_type, binding_context)

    @staticmethod
    @patch(pipes.__name__ + '.apply_attribute')
    def test_apply_every_attribute(apply_attribute_mock):
        """should call apply_attribute for every attribute"""
        xml_node = Mock()
        xml_node.attrs = [Mock(), Mock()]
        node = Node(xml_node)
        context = RenderingContext()

        apply_attributes(node, context)

        calls = [call(node, attr) for attr in xml_node.attrs]
        assert apply_attribute_mock.call_args_list == calls
