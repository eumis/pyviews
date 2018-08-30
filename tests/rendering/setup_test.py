from unittest import TestCase, main
from unittest.mock import Mock
from pyviews.testing import case
from pyviews.core.node import Node, Property
from pyviews.rendering.setup import NodeSetup

class NodeSetupTests(TestCase):
    @case(None, {})
    @case(lambda node: None, {})
    @case(lambda node: {}, {})
    @case(lambda node: {'one': 1, 'two': 'value'}, {'one': 1, 'two': 'value'})
    def test_get_child_args(self, get_child_args, expected_args):
        setup = NodeSetup(get_child_args=get_child_args)

        actual_args = setup.get_child_init_args(Mock())

        msg = 'get_child_args should return write args'
        self.assertDictEqual(actual_args, expected_args, msg)

    @case(Mock(), {}, Mock())
    @case(lambda *args: None, {'key': Property('')}, lambda node: None)
    def test_apply_should_setup_node(self, setter, properties: dict, on_destroy):
        node = Node(Mock())
        node_setup = NodeSetup(setter=setter, properties=properties, on_destroy=on_destroy)

        node_setup.apply(node)

        msg = 'apply should set setter'
        self.assertEqual(node.setter, setter, msg)

        msg = 'apply should set properties'
        self.assertListEqual(list(node.properties.keys()), list(properties.keys()), msg)

        msg = 'apply should set on_destroy'
        self.assertEqual(node.on_destroy, on_destroy, msg)

    def test_apply_shold_skip_empty_setup(self):
        node = Node(Mock())
        node.setter = lambda *args: None
        node.properties = {}
        node_setup = NodeSetup()

        node_setup.apply(node)

        msg = 'apply should skip empty setter'
        self.assertIsNotNone(node.setter, msg)

        msg = 'apply should skip empty properties'
        self.assertIsNotNone(node.properties, msg)

if __name__ == '__main__':
    main()
