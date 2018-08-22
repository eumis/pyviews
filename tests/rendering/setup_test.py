from unittest import TestCase, main
from unittest.mock import Mock
from pyviews.testing import case
from pyviews.rendering.setup import NodeSetup

class NodeSetupTests(TestCase):
    @case(None, {})
    @case(lambda node: None, {})
    @case(lambda node: {}, {})
    @case(lambda node: {'one': 1, 'two': 'value'}, {'one': 1, 'two': 'value'})
    def test_get_child_args(self, get_child_init_args, expected_args):
        setup = NodeSetup(get_child_init_args=get_child_init_args)

        actual_args = setup.get_child_init_args(Mock())

        msg = 'get_child_init_args should return write args'
        self.assertDictEqual(actual_args, expected_args, msg)

if __name__ == '__main__':
    main()
