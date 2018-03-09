from unittest import TestCase, main
from unittest.mock import Mock, call
from tests.utility import case
from pyviews.core.ioc import Scope, register_single
from pyviews.core.xml import XmlNode
from pyviews.core.node import Node, NodeArgs
from pyviews.core.observable import InheritedDict

class NodeArgsTests(TestCase):
    def test_get_args(self):
        xml_node = XmlNode('namespace', 'root')
        node = Node(xml_node)
        args = NodeArgs(xml_node, node).get_args(Node)

        msg = 'NodeArgs should return XmlNode as args'
        self.assertEqual([xml_node], args.args, msg)

        msg = 'NodeArgs should return parent as kwargs'
        self.assertEqual({'parent_context': node.context}, args.kwargs, msg)

class NodeTests(TestCase):
    def setUp(self):
        self.xml_node = XmlNode('namespace', 'root')
        self.node = Node(self.xml_node)

    def test_init_xml_node(self):
        msg = 'Node should inititalise properties from init parameters'
        self.assertEqual(self.node.xml_node, self.xml_node, msg)

    @case({'one': InheritedDict(), 'two': 1, 'three': InheritedDict()})
    @case({'key': InheritedDict()})
    @case({'key': 'value'})
    def test_context_setup(self, parent_context):
        node = Node(self.xml_node, parent_context=parent_context)
        msg = 'All values should be inherited from parent context'
        for key, value in parent_context.items():
            if isinstance(value, InheritedDict):
                self.assertEqual(node.context[key]._parent, value, msg)
            else:
                self.assertEqual(node.context[key], value, msg)

    def test_globals_property(self):
        msg = 'Globals property should be get from context'
        self.assertEqual(self.node.globals, self.node.context['globals'], msg)

    def test_globals_values(self):
        msg = 'Globals should contain node'
        self.assertEqual(self.node, self.node.globals['node'], msg)

    def test_destroy_should_destroy_children(self):
        with Scope('NodeTests.destroy_should_destroy_children'):
            mocks = [Mock(), Mock(), Mock()]
            self.xml_node.children = mocks
            register_single('render', lambda xml_node, args: xml_node)

            self.node.render_children()
            self.node.destroy()

            msg = 'destroy should destroy children'
            for child in mocks:
                self.assertTrue(child.destroy.called, msg)

    def test_destroy_should_destroy_bindings(self):
        mocks = [Mock(), Mock(), Mock()]

        for binding in mocks:
            self.node.add_binding(binding)
        self.node.destroy()

        msg = 'destroy should destroy bindings'
        for binding in mocks:
            self.assertTrue(binding.destroy.called, msg)

    def test_get_node_args(self):
        xml_node = XmlNode('namespace', 'node')
        args = self.node.get_node_args(xml_node)

        msg = 'get_node_args should return args with passed xml_node'
        self.assertEqual(args['xml_node'], xml_node, msg)

        msg = 'get_node_args should return args with node'
        self.assertEqual(args['parent_node'], self.node, msg)

if __name__ == '__main__':
    main()
