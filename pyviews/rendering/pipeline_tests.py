from unittest import TestCase
from unittest.mock import Mock, call, patch
from pyviews.testing import case
from pyviews.core import XmlAttr, Node, InstanceNode
from pyviews.core.ioc import Scope, register_single, scope
from pyviews.binding import Binder, add_one_way_rules
from pyviews.compilation import CompiledExpression
from .common import RenderingError
from . import pipeline
from . import modifiers
from .pipeline import RenderingPipeline
from .pipeline import call_set_attr, get_setter
from .pipeline import apply_attribute, apply_attributes
from .pipeline import run_steps, get_pipeline


class run_steps_tests(TestCase):
    @case(0, {'one': 1})
    @case(1, {'one': 1})
    @case(3, {'one': 1, 'two': 'value'})
    def test_runs_all_steps(self, steps_count, args):
        node = Node(Mock())
        steps = [Mock() for _ in range(steps_count)]
        render_pipeline = RenderingPipeline(steps=steps)

        run_steps(node, render_pipeline, **args)

        msg = 'run_steps should call all steps with passed args'
        for step in steps:
            self.assertEqual(step.call_args, call(node, pipeline=render_pipeline, **args), msg)

    @case({'one': 'two'}, {'key': 'value'}, {'one': 'two', 'key': 'value'})
    @case({'key': 'args'}, {'key': 'value'}, {'key': 'value'})
    def test_uses_step_result_as_args(self, args, step_result, expected):
        node = Node(Mock())

        def step(_, **__): return step_result

        next_step = Mock()
        steps = [step, next_step]
        render_pipeline = RenderingPipeline(steps=steps)

        run_steps(node, render_pipeline, **args)

        msg = 'should use step result as args for next step'
        self.assertEqual(call(node, pipeline=render_pipeline, **expected), next_step.call_args, msg)


class get_pipeline_tests(TestCase):
    def test_should_return_default_setup(self):
        render_pipeline = RenderingPipeline()
        with Scope('test_get_pipeline_def'):
            register_single('pipeline', render_pipeline)

            node = Node(Mock())
            actual_setup = get_pipeline(node)

        msg = 'get_pipeline should return default setup'
        self.assertEqual(actual_setup, render_pipeline, msg)

    @case(Node, Node(Mock()))
    @case(InstanceNode, InstanceNode(Mock(), Mock()))
    def test_should_return_setup_by_node_type(self, node_type, node):
        render_pipeline = RenderingPipeline()
        with Scope('test_get_pipeline_node'):
            register_single('pipeline', render_pipeline, node_type)

            actual_setup = get_pipeline(node)

        msg = 'get_pipeline should return setup by node type'
        self.assertEqual(actual_setup, render_pipeline, msg)

    class OtherInstanceNode(InstanceNode):
        """Class for get_pipeline_tests"""
        pass

    @case(InstanceNode(XmlAttr('name'), Mock()))
    @case(OtherInstanceNode(XmlAttr('name'), Mock()))
    def test_returns_setup_by_instance_type(self, node: InstanceNode):
        render_pipeline = RenderingPipeline()
        with Scope('test_get_pipeline_inst'):
            register_single('pipeline', render_pipeline, node.instance.__class__)

            actual_setup = get_pipeline(node)

        msg = 'get_pipeline should return setup by instance type'
        self.assertEqual(actual_setup, render_pipeline, msg)

    def test_steps_order(self):
        inst_setup = RenderingPipeline()
        type_setup = RenderingPipeline()
        def_setup = RenderingPipeline()

        inst_node = Mock()
        inst_node.instance = Mock()
        cases = [
            (InstanceNode(XmlAttr(''), Mock()), inst_setup),
            (InstanceNode(Mock(), Mock()), type_setup),
            (inst_node, def_setup)
        ]

        with Scope('test_get_pipeline_order'):
            register_single('pipeline', inst_setup, XmlAttr)
            register_single('pipeline', type_setup, Node)
            register_single('pipeline', type_setup, InstanceNode)
            register_single('pipeline', def_setup)

            for node, expected_setup in cases:
                actual_setup = get_pipeline(node)

                msg = 'get_pipeline should try get in order: by instance, by node type, default'
                self.assertEqual(actual_setup, expected_setup, msg)

    def test_raises(self):
        node = Node(Mock())
        with Scope('test_get_pipeline_raises'):
            msg = 'get_pipeline should throw error in case pipeline is not registered'
            with self.assertRaises(RenderingError, msg=msg):
                get_pipeline(node)


class AttributesRenderingTests(TestCase):
    def setUp(self):
        with self._get_scope():
            binder = Binder()
            add_one_way_rules(binder)

            register_single('binder', binder)
            register_single('expression', CompiledExpression)

    @staticmethod
    def _get_scope():
        return Scope('AttributesRenderingTests')

    @staticmethod
    def _get_setter_mock(get_setter_mock):
        setter_mock = Mock()
        get_setter_mock.side_effect = lambda attr: setter_mock
        return setter_mock

    @patch(pipeline.__name__ + '.get_setter')
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

    @patch(pipeline.__name__ + '.get_setter')
    @case(XmlAttr('key', '{1}'), 'oneway', '1')
    @case(XmlAttr('one', 'oneway:{1 + 1}'), 'oneway', '1 + 1')
    @case(XmlAttr('one', 'twoways:{vm.prop}'), 'twoways', 'vm.prop')
    def test_apply_attribute_applies_binding(self, get_setter_mock, xml_attr, binding_type, expr_body):
        setter_mock = self._get_setter_mock(get_setter_mock)
        node = Node(Mock())
        binder = Mock()
        expected_args = {
            'node': node,
            'attr': xml_attr,
            'modifier': setter_mock,
            'expr_body': expr_body
        }

        with Scope('test_apply_attribute_binding'):
            register_single('binder', binder)
            register_single('expression', CompiledExpression)

            apply_attribute(node, xml_attr)

        msg = 'apply_attribute should apply binding'
        self.assertEqual(binder.apply.call_args, call(binding_type, **expected_args), msg)

    @patch(pipeline.__name__ + '.apply_attribute')
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
        node.attr_setter = node_setter
        key, value = ('key', 'value')

        call_set_attr(node, key, value)

        msg = 'default_setter should call node setter'
        self.assertEqual(node_setter.call_args, call(node, key, value), msg)

    @case(None, call_set_attr)
    @case(modifiers.__name__ + '.import_global', modifiers.import_global)
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
