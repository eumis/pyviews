from unittest import TestCase, main
from unittest.mock import Mock
from tests.utility import case
from pyviews.core.ioc import register_value
from pyviews.core.compilation import Expression, ExpressionVars

class TestExpressionVars(TestCase):
    def setUp(self):
        parent = ExpressionVars()
        parent['one'] = 1
        parent['two'] = 2
        self.parent = parent

        self.globs = ExpressionVars(ExpressionVars(parent))
        self.globs['two'] = 'two'
        self.globs['three'] = 'three'

    def test_globals_keys(self):
        self.assertEqual(self.globs['one'], 1, 'Globals should get values from parent')

        msg = 'Globals should get own value if key exists'
        self.assertEqual(self.globs['two'], 'two', msg)
        self.assertEqual(self.globs['three'], 'three', msg)

    def test_dictionary(self):
        msg = 'to_dictionary should return dictionary with all values'
        self.assertEqual(
            self.globs.to_dictionary(),
            {'one': 1, 'two': 'two', 'three': 'three'},
            msg)

    def test_remove_keys(self):
        self.globs.remove_key('two')
        self.globs.remove_key('three')

        msg = 'remove_key should remove own key'
        self.assertEqual(self.globs['two'], 2, msg)

        with self.assertRaises(KeyError, msg=msg):
            self.globs['three']

    @case('one', True)
    @case('two', True)
    @case('three', True)
    @case('key', False)
    def test_has_keys(self, key, expected):
        msg = 'has_key should return true for existant keys and false in other case'
        self.assertEqual(self.globs.has_key(key), expected, msg)

    @case('key')
    @case('hoho')
    @case('')
    @case(' ')
    def test_raises(self, key):
        with self.assertRaises(KeyError, msg='KeyError should be raised for unknown key'):
            self.globs[key]

    def test_notifying(self):
        callback = Mock()
        self.globs.observe('one', callback)
        self.parent['one'] = 2
        msg = 'change event should be raised if key changed in parent'
        self.assertTrue(callback.called, msg)

class TestExpression(TestCase):
    def setUp(self):
        register_value('expressions', {})

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
