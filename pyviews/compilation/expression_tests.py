#pylint: disable=missing-docstring, invalid-name

from unittest import TestCase
from pyviews.testing import case
from pyviews.core import CompilationError
from .expression import CompiledExpression

class EvalExpression_compile_tests(TestCase):
    @case('2 + 2', None, 4)
    @case('some_key', {'some_key': 1}, 1)
    @case('some_key - 1', {'some_key': 1}, 0)
    @case('str(some_key)', {'some_key': 1}, '1')
    @case('some_key', {'some_key': 'asdf'}, 'asdf')
    @case('some_key(some_value)', {'some_key': lambda val: val, 'some_value': 'value'}, 'value')
    def test_execute(self, code, params, expected):
        expression = CompiledExpression(code)

        actual = expression.execute(params)

        msg = 'execute should return expression result value'
        self.assertEqual(expected, actual, msg)

    @case('2/0')
    @case('print(some_variable)')
    def test_execute_raises(self, body):
        expression = CompiledExpression(body)

        msg = 'execute should raise CompilationError'
        with self.assertRaises(CompilationError, msg=msg):
            expression.execute()

class EvalExpression_get_object_tree_tests(TestCase):
    def test_object_tree(self):
        expression = CompiledExpression("str(vm.vm.int_value) + vm.vm.str_value + vm.str_value + vm.get()")

        root = expression.get_object_tree()

        self.assertEqual(root.key, 'root', 'root entry should have entry with "root" key')
        self.assertEqual(sorted([e.key for e in root.children]), sorted(['str', 'vm']), \
                         'root entry should contain children for local values')

        str_node = [entry for entry in root.children if entry.key == 'str'][0]
        self.assertEqual(sorted([e.key for e in str_node.children]), [], \
                         'variable entry shouldn''t contain children')

        vm_node = [entry for entry in root.children if entry.key == 'vm'][0]
        self.assertEqual(sorted([e.key for e in vm_node.children]), sorted(['vm', 'str_value', 'get']), \
                         'variable entry should contain attribute children')

        str_node = [entry for entry in vm_node.children if entry.key == 'str_value'][0]
        self.assertEqual(sorted([e.key for e in str_node.children]), [], \
                         'attribute entry shouldn''t contain children')

        vm_node = [entry for entry in vm_node.children if entry.key == 'vm'][0]
        self.assertEqual(sorted([e.key for e in vm_node.children]), \
                         sorted(['int_value', 'str_value']), \
                         'variable entry should contain attribute children')
