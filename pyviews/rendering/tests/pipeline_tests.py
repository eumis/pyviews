from unittest.mock import Mock, call

from injectool import SingletonResolver, add_resolver
from pytest import mark, fixture, raises, fail

from pyviews.code import Code
from pyviews.core import Node, XmlNode, Observable, InstanceNode, ViewInfo
from pyviews.rendering.common import RenderingContext, RenderingError, get_rendering_context
from pyviews.rendering.pipeline import RenderingPipeline, get_pipeline, create_instance, get_type, render, use_pipeline


class Inst:
    def __init__(self, xml_node, parent_node):
        self.xml_node = xml_node
        self.parent_node = parent_node

    def __eq__(self, other):
        return self.xml_node == other.xml_node and self.parent_node == other.parent_node


class InstReversed:
    def __init__(self, parent_node, xml_node):
        self.xml_node = xml_node
        self.parent_node = parent_node

    def __eq__(self, other):
        return self.xml_node == other.xml_node and self.parent_node == other.parent_node


class SecondInst:
    def __init__(self, xml_node, parent_node=None):
        self.xml_node = xml_node
        self.parent_node = parent_node

    def __eq__(self, other):
        return self.xml_node == other.xml_node and self.parent_node == other.parent_node


class ThirdInst:
    def __init__(self, xml_node=None, parent_node=None):
        self.xml_node = xml_node
        self.parent_node = parent_node

    def __eq__(self, other):
        return self.xml_node == other.xml_node and self.parent_node == other.parent_node


class FourthInst:
    def __init__(self, xml_node, *_, parent_node=None, **__):
        self.xml_node = xml_node
        self.parent_node = parent_node

    def __eq__(self, other):
        return self.xml_node == other.xml_node and self.parent_node == other.parent_node


class InstWithKwargs:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


@fixture
def pipeline_fixture(request):
    xml_node = XmlNode('pyviews.core', 'Node', view_info=ViewInfo('test', 1))
    request.cls.context = RenderingContext({'xml_node': xml_node})
    request.cls.pipeline = RenderingPipeline()


@mark.usefixtures('container_fixture', 'pipeline_fixture')
class RenderingPipelineTests:
    @mark.parametrize('namespace, tag, node_type, init_args', [
        ('pyviews.core', 'Node', Node, {}),
        ('pyviews.code', 'Code', Code, {'parent_node': Node(XmlNode('', ''))})
    ])
    def test_creates_node(self, namespace, tag, node_type, init_args):
        """should create node using namespace as module and tag name as node class name"""
        context = RenderingContext(init_args)
        context.xml_node = XmlNode(namespace, tag)

        node = self.pipeline.run(context)

        assert isinstance(node, node_type)
        assert node.xml_node == context.xml_node

    def test_creates_node_using_passed_method(self):
        """should create node using namespace as module and tag name as node class name"""
        create_node, node = Mock(), Mock()
        create_node.side_effect = lambda ctx: node if ctx == self.context else None
        pipeline = RenderingPipeline(create_node=create_node)

        actual = pipeline.run(self.context)

        assert actual == node

    def test_adds_pipe_info_to_error(self):
        """should handle errors"""
        pipe = Mock()
        pipe.side_effect = Exception()
        pipeline = RenderingPipeline(pipes=[pipe])

        try:
            pipeline.run(self.context)
        except RenderingError as err:
            assert f'Pipe: {pipe}' in err.infos
        except BaseException:
            fail()

    @mark.parametrize('name', [None, '', 'pipeline'])
    def test_adds_pipeline_name_to_error(self, name):
        """should handle errors"""
        pipe = Mock()
        pipe.side_effect = Exception()
        pipeline = RenderingPipeline(name=name, pipes=[pipe])

        try:
            pipeline.run(self.context)
        except RenderingError as err:
            assert f'Pipeline: {name}' in err.infos
        except BaseException:
            fail()

    @mark.parametrize('namespace, tag, inst_type', [
        ('pyviews.core.observable', 'Observable', Observable),
        (__name__, 'InstWithKwargs', InstWithKwargs)
    ])
    def test_creates_instance_node(self, namespace, tag, inst_type):
        """should create instance and wrap it with InstanceNode"""
        xml_node = XmlNode(namespace, tag)

        node = self.pipeline.run(RenderingContext({'xml_node': xml_node}))

        assert isinstance(node, InstanceNode)
        assert isinstance(node.instance, inst_type)

    @mark.parametrize('pipes_count', [0, 1, 5])
    def test_calls_pipes(self, pipes_count):
        """Should call pipes"""
        pipes = [Mock() for _ in range(pipes_count)]
        pipeline = RenderingPipeline(pipes=pipes)

        node = pipeline.run(self.context)

        for pipe in pipes:
            assert pipe.call_args == call(node, self.context)

    def test_sets_current_rendering_context(self):
        """should set current rendering context"""
        actual = Mock()
        pipes = [lambda *_: setattr(actual, 'value', get_rendering_context())]
        pipeline = RenderingPipeline(pipes=pipes)

        pipeline.run(self.context)

        assert actual.value == self.context


class GetTypeTests:
    """get_type() function tests"""

    @staticmethod
    @mark.parametrize('xml_node, expected', [
        (XmlNode(__name__, 'Inst'), Inst),
        (XmlNode('pyviews.core.observable', 'Observable'), Observable),
        (XmlNode(__name__, 'SecondInst'), SecondInst),
        (XmlNode('pyviews.core', 'Node'), Node)
    ])
    def test_returns_type(xml_node, expected):
        """should return type or module for xml_node"""
        actual = get_type(xml_node)

        assert actual == expected

    @staticmethod
    @mark.parametrize('xml_node', [
        (XmlNode(__name__, 'UnknownType')),
        (XmlNode('pyviews.core.observable', 'SomeClass')),
        (XmlNode('pyviews.some_module.node', 'Node'))
    ])
    def test_raises_for_not_existing_type(xml_node):
        """should raise RenderingError for type failed to import"""
        with raises(RenderingError):
            get_type(xml_node)


class CreateInstanceTests:
    """create_instance() function tests"""

    @staticmethod
    @mark.parametrize('inst_type, init_args, expected', [
        (Inst, {'xml_node': 1, 'parent_node': 'node'}, Inst(1, 'node')),
        (InstReversed, {'xml_node': 1, 'parent_node': 'node'}, InstReversed('node', 1)),
        (SecondInst, {'xml_node': 1, 'parent_node': 'node'}, SecondInst(1, parent_node='node')),
        (SecondInst, {'xml_node': 1}, SecondInst(1)),
        (ThirdInst, {'xml_node': 1, 'parent_node': 'node'}, ThirdInst(xml_node=1, parent_node='node')),
        (ThirdInst, {}, ThirdInst())
    ])
    def test_returns_instance(inst_type, init_args, expected):
        """should create and return instance of passed type"""
        actual = create_instance(inst_type, RenderingContext(init_args))

        assert actual == expected

    @staticmethod
    @mark.parametrize('inst_type, init_args', [
        (Inst, {}),
        (Inst, {'xml_node': 1}),
        (Inst, {'parent_node': 'node'}),
        (InstReversed, {'xml_node': 1}),
        (InstReversed, {'parent_node': 'node'}),
        (SecondInst, {}),
        (SecondInst, {'parent_node': 'node'})
    ])
    def test_raises_if_context_misses_argument(inst_type, init_args):
        """should raise RenderingError if there are no required arguments"""
        with raises(RenderingError):
            create_instance(inst_type, RenderingContext(init_args))


@mark.parametrize('inst_type, init_args', [
    (Inst, {'xml_node': 1, 'parent_node': 'node'}),
    (InstReversed, {'xml_node': 1, 'parent_node': 'node'}),
    (SecondInst, {'xml_node': 1, 'parent_node': 'node'}),
    (ThirdInst, {'xml_node': 1, 'parent_node': 'node'})
])
def test_create_inst(inst_type, init_args):
    """should create and return instance of passed type"""
    inst = create_instance(inst_type, RenderingContext(init_args))

    assert isinstance(inst, inst_type)


@fixture
def get_pipeline_fixture(request):
    request.cls.resolver = SingletonResolver()
    add_resolver(RenderingPipeline, request.cls.resolver)
    request.cls.pipeline = RenderingPipeline()


@mark.usefixtures('container_fixture', 'get_pipeline_fixture')
class GetPipelineTests:
    """get_pipeline() tests"""

    @mark.parametrize('xml_node, key', [
        (XmlNode('pyviews.core.node', 'Node'), 'pyviews.core.node.Node'),
        (XmlNode('pyviews.core.node', 'Node'), 'pyviews.core.node'),
        (XmlNode('pyviews.core.observable', 'Observable'), 'pyviews.core.observable.Observable'),
        (XmlNode('pyviews.core.observable', 'Observable'), 'pyviews.core.observable')
    ])
    def test_resolves_pipeline_by_xml_node_namespace_and_name(self, xml_node, key):
        """should resolve RenderingPipeline using namespace.name or namespace"""
        self.resolver.set_value(self.pipeline, key)

        actual = get_pipeline(xml_node)

        assert actual == self.pipeline

    def test_resolves_by_name_first(self):
        """should try resolve by namespace.name first"""
        name_pipeline, namespace_pipeline = RenderingPipeline(), RenderingPipeline()
        xml_node = XmlNode('pyviews.core.node', 'Node')
        self.resolver.set_value(namespace_pipeline, xml_node.namespace)
        self.resolver.set_value(name_pipeline, f'{xml_node.namespace}.{xml_node.name}')

        actual = get_pipeline(xml_node)

        assert actual == name_pipeline

    @staticmethod
    def test_raises_rendering_error_for_missed_pipeline():
        """should raise RenderingError if pipeline is not found"""
        with raises(RenderingError):
            get_pipeline(XmlNode('pyviews.core.node', 'Node'))


@fixture
def render_fixture(request):
    xml_node = XmlNode('pyviews.core.node', 'Node')
    pipeline = RenderingPipeline()
    pipeline_resolver = SingletonResolver()
    pipeline_resolver.set_value(pipeline, f'{xml_node.namespace}.{xml_node.name}')
    add_resolver(RenderingPipeline, pipeline_resolver)

    request.cls.xml_node = xml_node
    request.cls.pipeline = pipeline
    request.cls.pipeline_resolver = pipeline_resolver
    request.cls.context = RenderingContext({'xml_node': xml_node})


@mark.usefixtures('container_fixture', 'render_fixture')
class RenderTests:
    def _set_pipeline(self, xml_node, pipeline):
        self.pipeline_resolver.set_value(pipeline, f'{xml_node.namespace}.{xml_node.name}')

    @mark.parametrize('namespace, tag, node_type, init_args', [
        ('pyviews.core', 'Node', Node, {}),
        ('pyviews.code', 'Code', Code, {'parent_node': Node(XmlNode('', ''))})
    ])
    def test_runs_pipeline(self, namespace, tag, node_type, init_args):
        """should run pipeline and return node created by pipeline"""
        context = RenderingContext(init_args)
        context.xml_node = XmlNode(namespace, tag)
        self._set_pipeline(context.xml_node, RenderingPipeline())

        node = render(context)

        assert isinstance(node, node_type)
        assert node.xml_node == context.xml_node


@mark.usefixtures('container_fixture')
class UsePipelineTests:
    @mark.parametrize('class_path', ['package.module.class', 'package.module'])
    def test_adds_pipeline_to_passed_resolver(self, class_path: str):
        """should add pipeline to passed resolver"""
        resolver, pipeline = SingletonResolver(), RenderingPipeline()

        use_pipeline(pipeline, class_path, resolver)

        assert resolver.resolve(self.container, class_path) == pipeline

    @mark.parametrize('class_path', ['package.module.class', 'package.module'])
    def test_adds_pipeline_to_resolver_from_container(self, class_path: str):
        """should add pipeline to passed resolver"""
        resolver, pipeline = SingletonResolver(), RenderingPipeline()
        add_resolver(RenderingPipeline, resolver)

        use_pipeline(pipeline, class_path)

        assert resolver.resolve(self.container, class_path) == pipeline
