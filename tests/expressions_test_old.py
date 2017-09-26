from unittest import TestCase, main
from tests.mock import TestViewModel, TestNode
from tests.utility import case
from pyviews.common import expressions as tested
from pyviews import application
from pyviews.common import ioc

application.setup_ioc()

class TestExpressions(TestCase):
    @case('{asdf}', True)
    @case('{{asdf}}', True)
    @case('{asdf', False)
    @case('asdf}', False)
    @case(' {asdf}', False)
    def test_isbinding(self, expr, expected):
        self.assertEqual(tested.is_binding(expr), expected)

    @case('{asdf}', 'asdf')
    @case('asdf', 'sd')
    def test_parse_one_way_binding(self, expr, expected):
        self.assertEqual(tested.parse_one_way_binding(expr), expected)

    def test_to_dictionary(self):
        view_model = TestViewModel()
        view_model.value = 1
        view_model._private_prop = 'value'
        vm_dict = tested.to_dictionary(view_model)
        self.assertEqual(vm_dict['name'], None)
        self.assertEqual(vm_dict['value'], 1)
        self.assertFalse('_private_prop' in vm_dict)

    @case('package.module.name', ('package.module', 'name'))
    @case('package.module', ('package', 'module'))
    @case('package', ('', 'package'))
    def test_split_by_last_dot(self, name, expected):
        self.assertEqual(tested.split_by_last_dot(name), expected)

    def test_eval_exp(self):
        expression = '{some expression}'
        node = TestNode()
        node.view_model = TestViewModel()
        node.context.globals['global_value'] = 1
        node.context.globals['method'] = lambda: 1

        ioc.register_value('run', lambda code, gl, lc, nd=node:
                           self._run(code, gl, lc, nd, 'some expression'))
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
