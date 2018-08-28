from unittest import TestCase, main
from unittest.mock import Mock, call, patch
from pyviews.testing import case
from pyviews.core.node import Node, InstanceNode
from pyviews.core.xml import XmlAttr
from pyviews.core.ioc import Scope, register_single, scope
from pyviews.rendering import RenderingError
from pyviews.rendering.modifiers import import_global
from pyviews.rendering.binding import BindingFactory, add_default_rules, BindingArgs
from pyviews.rendering.setup import NodeSetup
from pyviews.rendering.flow import default_setter, get_setter
from pyviews.rendering.flow import apply_attribute, apply_attributes
from pyviews.rendering.flow import run_steps, get_node_setup

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

    def test_get_node_setup_should_return_default_setup(self):
        node_setup = NodeSetup()
        with Scope('test_get_node_setup_def'):
            register_single('setup', node_setup)

            node = Node(Mock())
            actual_setup = get_node_setup(node)

        msg = 'get_node_setup should return default setup'
        self.assertEqual(actual_setup, node_setup, msg)

    @case(Node, Node(Mock()))
    @case(InstanceNode, InstanceNode(Mock(), Mock()))
    def test_get_node_setup_should_return_setup_by_node_type(self, node_type, node):
        node_setup = NodeSetup()
        with Scope('test_get_node_setup_node'):
            register_single('setup', node_setup, node_type)

            actual_setup = get_node_setup(node)

        msg = 'get_node_setup should return setup by node type'
        self.assertEqual(actual_setup, node_setup, msg)

    def test_get_node_setup_should_return_setup_by_instance_type(self):
        node_setup = NodeSetup()
        with Scope('test_get_node_setup_inst'):
            register_single('setup', node_setup, XmlAttr)
            node = InstanceNode(XmlAttr('name'), Mock())

            actual_setup = get_node_setup(node)

        msg = 'get_node_setup should return setup by instance type'
        self.assertEqual(actual_setup, node_setup, msg)

    def test_get_node_setup_order(self):
        inst_setup = NodeSetup()
        type_setup = NodeSetup()
        def_setup = NodeSetup()

        inst_node = Mock()
        inst_node.instance = Mock()
        cases = [
            (InstanceNode(XmlAttr(''), Mock()), inst_setup),
            (InstanceNode(Mock(), Mock()), type_setup),
            (inst_node, def_setup)
        ]

        with Scope('test_get_node_setup_order'):
            register_single('setup', inst_setup, XmlAttr)
            register_single('setup', type_setup, Node)
            register_single('setup', type_setup, InstanceNode)
            register_single('setup', def_setup)

            for node, expected_setup in cases:
                actual_setup = get_node_setup(node)

                msg = 'get_node_setup should try get in order: by instance, by node type, default'
                self.assertEqual(actual_setup, expected_setup, msg)

    def test_get_node_setup_raises(self):
        node = Node(Mock())
        with Scope('test_get_node_setup_raises'):
            msg = 'get_node_setup should throw error in case node_setup is not registered'
            with self.assertRaises(RenderingError, msg=msg):
                get_node_setup(node)


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

    @scope('modifier_tests')
    @case('', '')
    @case('', 'attr_name')
    @case('tests.rendering.core_test.some_modifier_not', 'attr_name')
    def test_get_setter_raises(self, namespace, name):
        msg = 'get_setter should raise ImportError if namespace can''t be imported'
        with self.assertRaises(ImportError, msg=msg):
            xml_attr = XmlAttr(name, '', namespace)
            get_setter(xml_attr)

if __name__ == '__main__':
    main()
