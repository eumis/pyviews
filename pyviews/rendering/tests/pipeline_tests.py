from unittest.mock import Mock, call, patch

from injectool import make_default, add_singleton, SingletonResolver, add_resolver, add_resolve_function
from pytest import mark, fixture, raises

from pyviews.binding import Binder, OnceRule, OnewayRule
from pyviews.compilation import CompiledExpression
from pyviews.core import XmlAttr, Node, InstanceNode, Expression
from pyviews.rendering import modifiers
from pyviews.rendering import pipeline
from pyviews.rendering.common import RenderingError
from pyviews.rendering.pipeline import RenderingPipeline
from pyviews.rendering.pipeline import apply_attribute, apply_attributes
from pyviews.rendering.pipeline import call_set_attr, get_setter
from pyviews.rendering.pipeline import run_steps, get_pipeline


class RunStepsTests:
    """run_steps() tests"""

    @mark.parametrize('steps_count, args', [
        (0, {'one': 1}),
        (1, {'one': 1}),
        (3, {'one': 1, 'two': 'value'})
    ])
    def test_runs_all_steps(self, steps_count, args):
        """run_steps should call all steps with passed args"""
        node = Node(Mock())
        steps = [Mock() for _ in range(steps_count)]
        render_pipeline = RenderingPipeline(steps=steps)

        run_steps(node, render_pipeline, **args)

        for step in steps:
            assert step.call_args == call(node, pipeline=render_pipeline, **args)

    @mark.parametrize('args, step_result, expected', [
        ({'one': 'two'}, {'key': 'value'}, {'one': 'two', 'key': 'value'}),
        ({'key': 'args'}, {'key': 'value'}, {'key': 'value'})
    ])
    def test_uses_step_result_as_args(self, args, step_result, expected):
        """should use step result as args for next step"""
        node = Node(Mock())

        def step(_, **__):
            return step_result

        next_step = Mock()
        steps = [step, next_step]
        render_pipeline = RenderingPipeline(steps=steps)

        run_steps(node, render_pipeline, **args)

        assert call(node, pipeline=render_pipeline, **expected) == next_step.call_args


class GetPipelineTests:
    """get_pipeline() tests"""

    @staticmethod
    def test_returns_default_setup():
        """should return default setup"""
        render_pipeline = RenderingPipeline()
        with make_default('test_get_pipeline_def'):
            add_singleton(RenderingPipeline, render_pipeline)

            node = Node(Mock())
            actual_setup = get_pipeline(node)

        assert actual_setup == render_pipeline

    @mark.parametrize('node_type, node', [
        (Node, Node(Mock())),
        (InstanceNode, InstanceNode(Mock(), Mock()))
    ])
    def test_should_return_setup_by_node_type(self, node_type, node):
        """should return setup by node type"""
        render_pipeline = RenderingPipeline()
        with make_default('test_get_pipeline_node'):
            add_resolver(RenderingPipeline, SingletonResolver(render_pipeline, node_type))

            actual_setup = get_pipeline(node)

        assert actual_setup == render_pipeline

    class OtherInstanceNode(InstanceNode):
        """Class for get_pipeline_tests"""
        pass

    @mark.parametrize('node', [
        (InstanceNode(XmlAttr('name'), Mock())),
        (OtherInstanceNode(XmlAttr('name'), Mock()))
    ])
    def test_returns_setup_by_instance_type(self, node: InstanceNode):
        """get_pipeline should return setup by instance type"""
        render_pipeline = RenderingPipeline()
        with make_default('test_get_pipeline_inst'):
            add_resolver(RenderingPipeline, SingletonResolver(render_pipeline, node.instance.__class__))

            actual_setup = get_pipeline(node)

        assert actual_setup == render_pipeline

    @staticmethod
    def test_steps_order():
        """should try get in order: by instance, by node type, default"""
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

        with make_default('test_get_pipeline_order'):
            resolver = SingletonResolver(def_setup)
            resolver.add_value(type_setup, Node)
            resolver.add_value(type_setup, InstanceNode)
            resolver.add_value(inst_setup, XmlAttr)
            add_resolver(RenderingPipeline, resolver)

            for node, expected_setup in cases:
                actual_setup = get_pipeline(node)

                assert actual_setup == expected_setup

    @staticmethod
    def test_raises():
        """should throw error in case pipeline is not registered"""
        node = Node(Mock())
        with make_default('test_get_pipeline_raises'):
            with raises(RenderingError):
                get_pipeline(node)


@fixture(scope='function')
def apply_attribute_fixture(request):
    setter_mock = Mock()
    get_setter_mock = Mock()
    get_setter_mock.side_effect = lambda attr: setter_mock
    request.cls.setter_mock = setter_mock
    with patch(pipeline.__name__ + '.get_setter', get_setter_mock):
        with make_default('bind_fixture_scope') as fixture_scope:
            binder = Binder()
            binder.add_rule('once', OnceRule())
            binder.add_rule('oneway', OnewayRule())
            add_singleton(Binder, binder)
            add_resolve_function(Expression, lambda c, p=None: CompiledExpression(p))
            yield fixture_scope


@mark.usefixtures('apply_attribute_fixture')
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
        expected_args = {
            'node': node,
            'attr': xml_attr,
            'modifier': self.setter_mock,
            'expr_body': expr_body
        }

        apply_attribute(node, xml_attr)
        assert binder.apply.call_args == call(binding_type, **expected_args)

    @patch(pipeline.__name__ + '.apply_attribute')
    def test_apply_every_attribute(self, apply_attribute_mock):
        """should call apply_attribute for every attribute"""
        xml_node = Mock()
        xml_node.attrs = [Mock(), Mock()]
        node = Node(xml_node)

        apply_attributes(node)

        calls = [call(node, attr) for attr in xml_node.attrs]
        assert apply_attribute_mock.call_args_list == calls


class GetSetterTests:
    """get_setter() tests"""

    @staticmethod
    def test_default_setter():
        """should call node setter"""
        node = Node(Mock())
        node_setter = Mock()
        node.attr_setter = node_setter
        key, value = ('key', 'value')

        call_set_attr(node, key, value)

        assert node_setter.call_args == call(node, key, value)

    @mark.parametrize('setter_path, expected_setter', [
        (None, call_set_attr),
        (modifiers.__name__ + '.import_global', modifiers.import_global)
    ])
    def test_returns_setter(self, setter_path, expected_setter):
        """should return appropriate setter"""
        actual_setter = get_setter(XmlAttr('', namespace=setter_path))

        assert actual_setter == expected_setter

    @staticmethod
    @mark.parametrize('namespace, name', [
        ('', ''),
        ('', 'attr_name'),
        ('tests.rendering.core_test.some_modifier_not', 'attr_name')
    ])
    def test_raises(namespace, name):
        """should raise ImportError if namespace can''t be imported"""
        with raises(ImportError):
            xml_attr = XmlAttr(name, '', namespace)
            get_setter(xml_attr)
