from unittest.mock import Mock

from _pytest.fixtures import fixture
from pytest import mark

from pyviews.binding_node import BindingNode, apply_attributes, BindingProperty, set_target
from pyviews.core import XmlNode, XmlAttr, InheritedDict
from pyviews.expression import Expression
from pyviews.pipes import get_setter
from pyviews.rendering import RenderingContext


class BindingNodeTests:
    @staticmethod
    def test_destroy():
        """should destroy binding"""
        node = BindingNode(Mock())
        binding = Mock()
        node.binding = binding

        node.destroy()

        assert binding.destroy.called
        assert node.binding is None


@fixture
def node_fixture(request):
    xml_node = XmlNode('', 'Binding', attrs=[])
    node = BindingNode(xml_node, InheritedDict())

    request.cls.xml_node = xml_node
    request.cls.node = node


@mark.usefixtures('node_fixture')
class ApplyAttributesTests:
    @mark.parametrize('value, code', [('{vm.property}', 'vm.property')])
    def test_when_attribute(self, value, code):
        """should parse value as expression"""
        self.xml_node.attrs.append(XmlAttr('when', value))

        apply_attributes(self.node, Mock())

        assert isinstance(self.node.when, Expression)
        assert self.node.when.code == code

    @mark.parametrize('attr_value, value', [
        ('{True}', True),
        ('{False}', False)
    ])
    def test_execute_on_bind(self, attr_value, value):
        """should set value"""
        self.xml_node.attrs.append(XmlAttr('execute_on_bind', attr_value))

        apply_attributes(self.node, Mock())

        assert self.node.execute_on_bind == value

    @mark.parametrize('value, target', [
        ('{target}', Mock())
    ])
    def test_target(self, value, target):
        """should set target"""
        self.xml_node.attrs.append(XmlAttr('target', value))
        self.node.node_globals['target'] = target

        apply_attributes(self.node, Mock())

        assert self.node.target == target

    def test_properties(self):
        """should add properties setters"""
        attr = XmlAttr('some_key', 'some value')
        self.xml_node.attrs.append(attr)
        setter = get_setter(attr)

        apply_attributes(self.node, Mock())

        assert self.node.properties == [BindingProperty(attr.name, setter, attr.value)]


class SetTargetTests:
    @staticmethod
    def test_uses_parent_node():
        """should set parent_node as target"""
        node, parent_node = BindingNode(Mock()), Mock()
        context = RenderingContext({'parent_node': parent_node})

        set_target(node, context)

        assert node.target == parent_node

    @staticmethod
    def test_skips():
        """should skip in case target is set"""
        node, parent_node = BindingNode(Mock()), Mock()
        node.target = Mock()
        context = RenderingContext({'parent_node': parent_node})

        set_target(node, context)

        assert node.target != parent_node
