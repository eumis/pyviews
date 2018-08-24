from unittest import TestCase, main
from unittest.mock import Mock, call, patch
from pyviews.testing import case
from pyviews.core.node import Node
from pyviews.core.xml import XmlAttr
from pyviews.core.ioc import Scope, register_single
from pyviews.rendering.modifiers import import_global
from pyviews.rendering.binding import BindingFactory, add_default_rules, BindingArgs
from pyviews.rendering.setup import NodeSetup
from pyviews.rendering.flow import default_setter, get_setter
from pyviews.rendering.flow import apply_attribute, apply_attributes
from pyviews.rendering.flow import run_steps

class RenderingTests(TestCase):
    @case(0, {'one': 1})
    @case(1, {'one': 1})
    @case(3, {'one': 1, 'two': 'value'})
    def test_run_steps_runs_all_steps(self, steps_count, args):
        node = Node(Mock())
        steps = [Mock() for i in range(steps_count)]
        node_setup = NodeSetup(render_steps=steps)

        run_steps(node, node_setup, **args)

        msg = 'run_steps should call all steps with passed args'
        for step in steps:
            self.assertEqual(step.call_args, call(node, node_setup=node_setup, **args), msg)

class AttributesRenderingTests(TestCase):
    def setUp(self):
        with self._get_scope():
            factory = BindingFactory()
            add_default_rules(factory)

            register_single('binding_factory', factory)

    def _get_scope(self):
        return Scope('AttributesRenderingTests')

    def _get_setter_mock(self, get_setter_mock):
        setter_mock = Mock()
        get_setter_mock.side_effect = lambda attr: setter_mock
        return setter_mock

    @patch('pyviews.rendering.flow.get_setter')
    @case(XmlAttr('key', 'value'), 'key', 'value')
    @case(XmlAttr('', 'value'), '', 'value')
    @case(XmlAttr('one', '{1}'), 'one', 1)
    @case(XmlAttr('one', 'once:{1 + 1}'), 'one', 2)
    def test_apply_attribute_calls_setter(self, get_setter_mock, xml_attr: XmlAttr, key, value):
        setter_mock = self._get_setter_mock(get_setter_mock)
        node = Node(Mock())

        with self._get_scope():
            apply_attribute(node, xml_attr)

        msg = 'apply_attribute should call setter'
        self.assertEqual(setter_mock.call_args, call(node, key, value), msg)

    @patch('pyviews.rendering.flow.get_setter')
    @case(XmlAttr('key', '{1}'), 'oneway', '1')
    @case(XmlAttr('one', 'oneway:{1 + 1}'), 'oneway', '1 + 1')
    @case(XmlAttr('one', 'twoways:{vm.prop}'), 'twoways', 'vm.prop')
    def test_apply_attribute_saves_binding(self, get_setter_mock, xml_attr, binding_type, expr_body):
        setter_mock = self._get_setter_mock(get_setter_mock)
        node = Node(Mock())
        apply_binding_mock = Mock()
        factory = BindingFactory()
        factory.add_rule(binding_type, BindingFactory.Rule(lambda args: True, apply_binding_mock))

        with Scope('test_apply_attribute_binding'):
            register_single('binding_factory', factory)

            apply_attribute(node, xml_attr)

        msg = 'apply_attribute should apply binding'
        binding_args = BindingArgs(node, xml_attr, setter_mock, expr_body)
        self.assertEqual(apply_binding_mock.call_args, call(binding_args), msg)

    @patch('pyviews.rendering.flow.apply_attribute')
    def test_apply_attributes_apply_every_attribute(self, apply_attribute_mock):
        xml_node = Mock()
        xml_node.attrs = [Mock(), Mock()]
        node = Node(xml_node)

        apply_attributes(node)

        msg = 'apply_attributes should call apply_attribute for every attribute'
        calls = [call(node, attr) for attr in xml_node.attrs]
        self.assertEqual(apply_attribute_mock.call_args_list, calls, msg)

class SetterTests(TestCase):
    def test_default_setter_should_call_node_setter(self):
        node = Node(Mock())
        node_setter = Mock()
        node.setter = node_setter
        key, value = ('key', 'value')

        default_setter(node, key, value)

        msg = 'default_setter should call node setter'
        self.assertEqual(node_setter.call_args, call(node, key, value), msg)

    @case(None, default_setter)
    @case('pyviews.rendering.modifiers.import_global', import_global)
    def test_get_setter_returns_setter(self, setter_path, expected_setter):
        actual_setter = get_setter(XmlAttr('', namespace=setter_path))

        msg = 'get_setter should return appropriate setter'
        self.assertEqual(actual_setter, expected_setter, msg)

if __name__ == '__main__':
    main()
