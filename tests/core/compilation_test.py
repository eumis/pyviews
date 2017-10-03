from unittest import TestCase, main
from tests.utility import case
from pyviews.core.compilation import Expression, ExpressionVars

class TestExpressionVars(TestCase):
    def test_globals_keys(self):
        parent = ExpressionVars()
        parent['one'] = 1
        parent['two'] = 2

        globs = ExpressionVars(parent)
        globs['two'] = 'two'
        globs['three'] = 'three'

        self.assertEqual(globs['one'], 1, 'Globals should get values from parent')
        msg = 'Globals should get own value if key exists'
        self.assertEqual(globs['two'], 'two', msg)
        self.assertEqual(globs['three'], 'three', msg)

    def test_parent_keys(self):
        parent = ExpressionVars()
        parent['one'] = 1
        parent['two'] = 2

        globs = ExpressionVars(parent)
        globs['two'] = 'two'
        globs['three'] = 'three'

        msg = 'own_keys should return only own keys'
        self.assertEqual(sorted(globs.own_keys()), sorted(['two', 'three']), msg)

        msg = 'all_keys should return own keys plus parent keys'
        self.assertEqual(sorted(globs.all_keys()), sorted(['one', 'two', 'three']), msg)

    def test_dictionary(self):
        parent = ExpressionVars()
        parent['one'] = 1
        parent['two'] = 2

        globs = ExpressionVars(parent)
        globs['two'] = 'two'
        globs['three'] = 'three'

        msg = 'to_dictionary should return dictionary with own keys'
        self.assertEqual(globs.to_dictionary(), {'two': 'two', 'three': 'three'}, msg)

        msg = 'to_all_dictionary should return dictionary with all keys'
        self.assertEqual(globs.to_all_dictionary(), {'one': 1, 'two': 'two', 'three': 'three'}, msg)

class TestExpression(TestCase):
    @case('2 + 2', None, 4)
    @case('some_key', {'some_key': 1}, 1)
    @case('some_key - 1', {'some_key': 1}, 0)
    @case('str(some_key)', {'some_key': 1}, '1')
    @case('some_key', {'some_key': 'asdf'}, 'asdf')
    @case('some_key(some_value)', {'some_key': lambda val: val, 'some_value': 'value'}, 'value')
    def test_compile_result(self, code, params, expected):
        expression = Expression(code)
        msg = 'compile should return expression result value'
        self.assertEqual(expression.execute(params), expected, msg)

    def test_var_tree(self):
        expression = Expression("str(vm.vm.int_value) + vm.vm.str_value + vm.str_value")

        root = expression.get_var_tree()

        self.assertEqual(root.key, 'root', 'root entry should have entry with "root" key')
        self.assertEqual(sorted([e.key for e in root.entries]), sorted(['str', 'vm']), \
                         'root entry should contain entries for local values')

        str_node = [entry for entry in root.entries if entry.key == 'str'][0]
        self.assertEqual(sorted([e.key for e in str_node.entries]), [], \
                         'variable entry shouldn''t contain children')

        vm_node = [entry for entry in root.entries if entry.key == 'vm'][0]
        self.assertEqual(sorted([e.key for e in vm_node.entries]), sorted(['vm', 'str_value']), \
                         'variable entry should contain attribute entries')

        str_node = [entry for entry in vm_node.entries if entry.key == 'str_value'][0]
        self.assertEqual(sorted([e.key for e in str_node.entries]), [], \
                         'attribute entry shouldn''t contain entries')

        vm_node = [entry for entry in vm_node.entries if entry.key == 'vm'][0]
        self.assertEqual(sorted([e.key for e in vm_node.entries]), \
                         sorted(['int_value', 'str_value']), \
                         'variable entry should contain attribute entries')

if __name__ == '__main__':
    main()
