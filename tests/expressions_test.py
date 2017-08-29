from unittest import TestCase, main
import pyviews.common.expressions as tested
from pyviews import application
from pyviews.common import ioc
from tests.mock import TestViewModel, TestNode

application.setup_ioc()

class TestExpressions(TestCase):
    def test_isbinding(self):
        self.assertTrue(tested.is_binding('{asdf}'))
        self.assertTrue(tested.is_binding('{{asdf}}'))
        self.assertFalse(tested.is_binding('{asdf'))
        self.assertFalse(tested.is_binding('asdf}'))
        self.assertFalse(tested.is_binding(' {asdf}'))

    def test_parse_one_way_binding(self):
        self.assertEqual(tested.parse_one_way_binding('{asdf}'), 'asdf')
        self.assertEqual(tested.parse_one_way_binding('asdf'), 'sd')

    def test_to_dictionary(self):
        view_model = TestViewModel()
        view_model.value = 1
        view_model._private_prop = 'value'
        vm_dict = tested.to_dictionary(view_model)
        self.assertEqual(vm_dict['name'], None)
        self.assertEqual(vm_dict['value'], 1)
        self.assertFalse('_private_prop' in vm_dict)

    def test_split_by_last_dot(self):
        self.assertEqual(tested.split_by_last_dot('package.module.name'), ('package.module', 'name'))
        self.assertEqual(tested.split_by_last_dot('package.module'), ('package', 'module'))
        self.assertEqual(tested.split_by_last_dot('package'), ('', 'package'))

    def test_eval_exp(self):
        expression = '{some expression}'
        node = TestNode()
        node.view_model = TestViewModel()
        node.context.globals['global_value'] = 1
        node.context.globals['method'] = lambda: 1

        ioc.register_value('run', lambda code, gl, lc, nd=node: self._run(code, gl, lc, nd, 'some expression'))
        ioc.register_value('node_key', 'node')
        ioc.register_value('vm_key', 'vm')

        tested.eval_exp(expression, node)

    def _run(self, code, globals_, locals_, actual_node, actual_code):
        self.assertEqual(code, actual_code)
        self.assertEqual(locals_, {})
        self.assertEqual(globals_['node'], actual_node)
        self.assertEqual(globals_['vm'], actual_node.view_model)
        
        for key in actual_node.view_model.get_observable_keys():
            self.assertEqual(globals_[key], getattr(actual_node.view_model, key))

        for key in actual_node.context.globals:
            self.assertEqual(globals_[key], actual_node.context.globals[key])

if __name__ == '__main__':
    main()
