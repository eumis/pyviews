from unittest import TestCase, main
from unittest.mock import Mock, call
from tests.mock import some_modifier
from pyviews.testing import case
from pyviews.core.xml import XmlNode, XmlAttr
from pyviews.core.node import Node, RenderArgs
from pyviews.core.ioc import Scope, register_single, scope
from pyviews.rendering import core
from pyviews.rendering.dependencies import register_defaults

class NodeRenderingTests(TestCase):
    def setUp(self):
        xml_node = XmlNode('pyviews.core.node', 'Node')
        self.parent_node = Node(xml_node)

        self.xml_node = XmlNode('pyviews.core.node', 'Node')
        with Scope('NodeRenderingTests'):
            register_defaults()

    @scope('NodeRenderingTests')
    def test_render(self):
        self.parent_node.globals['some_key'] = 'some value'

        node = core.render_old(self.xml_node, RenderArgs(self.xml_node, self.parent_node))

        msg = 'parse should init node with right passed xml_node'
        self.assertIsInstance(node, Node, msg=msg)

        msg = 'parse should init node with passed parent'
        self.assertEqual(node.globals['some_key'], 'some value', msg=msg)

class SomeObject:
    def __init__(self):
        pass

class ParseObjectNodeTests(TestCase):
    def setUp(self):
        self.xml_node = XmlNode('tests.rendering.core_test', 'SomeObject')
        with Scope('ParseObjectNodeTests'):
            register_defaults()

    @scope('ParseObjectNodeTests')
    def test_parse_raises(self):
        msg = 'parse should raise error if method "convert_to_node" is not registered'
        with self.assertRaises(core.RenderingError, msg=msg):
            core.render_old(self.xml_node, core.RenderArgs(self.xml_node))

def set_attr():
    pass

class GetModifierTests(TestCase):
    def setUp(self):
        with Scope('modifier_tests'):
            register_single('set_attr', set_attr)

    @scope('modifier_tests')
    @case(None, '', set_attr)
    @case(None, 'attr_name', set_attr)
    @case('tests.rendering.core_test.some_modifier', '', some_modifier)
    @case('tests.rendering.core_test.some_modifier', 'attr_name', some_modifier)
    def test_get_modifier(self, namespace, name, expected):
        xml_attr = XmlAttr(name, '', namespace)
        actual = core.get_modifier(xml_attr)
        self.assertEqual(actual, expected)

    @scope('modifier_tests')
    @case('', '')
    @case('', 'attr_name')
    @case('tests.rendering.core_test.some_modifier_not', 'attr_name')
    def test_get_modifier_raises(self, namespace, name):
        msg = 'get_modifier should raise ImportError if namespace can''t be imported'
        with self.assertRaises(ImportError, msg=msg):
            xml_attr = XmlAttr(name, '', namespace)
            core.get_modifier(xml_attr)

class RenderStepTests(TestCase):
    @case({})
    @case({'key': 1})
    def test_render_step(self, args):
        step = Mock()
        decorated_step = core.render_step(step)
        node = Mock()

        decorated_step(node, args)

        msg = 'render_step pass node to step'
        self.assertEqual(step.call_args, call(node), msg)

    @case({})
    @case({'key': 1, 'key2': 'value'})
    def test_render_step_with_parameters(self, args):
        step = Mock()
        decorated_step = core.render_step(*args.keys())(step)
        node = Mock()

        decorated_step(node, args)

        msg = 'render_step should pass args to step'
        self.assertEqual(step.call_args, call(node, **args), msg)

if __name__ == '__main__':
    main()
