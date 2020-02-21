from pytest import mark, raises, fixture

from pyviews.expression import Expression, ExpressionError
from pyviews.expression.expression import execute


@fixture
def object_tree_fixture(request):
    expression = Expression("str(vm.vm.int_value) + vm.vm.str_value + vm.str_value + vm.get()")
    root = expression.get_object_tree()

    request.cls.root = root
    request.cls.vm_node = [entry for entry in root.children if entry.key == 'vm'][0]


@mark.usefixtures('object_tree_fixture')
class ExpressionTests:

    def test_root(self):
        """get_object_tree() should return objects tree root"""
        assert self.root.key == 'root'

    def test_locals(self):
        """get_object_tree(): root should contain local variables"""
        assert sorted([e.key for e in self.root.children]) == sorted(['str', 'vm'])

    def test_method(self):
        """get_object_tree(): method node should not contain any child"""
        str_method_node = [entry for entry in self.root.children if entry.key == 'str'][0]

        assert [e.key for e in str_method_node.children] == []

    def test_property(self):
        """get_object_tree(): object node should have children node for property"""
        assert sorted([e.key for e in self.vm_node.children]) == sorted(['vm', 'str_value', 'get'])

    def test_empty_children(self):
        """
        get_object_tree(): object node should not have children
        if there are no properties used in expression
        """
        str_value_node = [entry for entry in self.vm_node.children if entry.key == 'str_value'][0]

        assert [e.key for e in str_value_node.children] == []

    def test_property_children(self):
        """
        get_object_tree(): object node should have children
        if there are its properties used in expression
        """
        inner_vm_node = [entry for entry in self.vm_node.children if entry.key == 'vm'][0]

        assert sorted([e.key for e in inner_vm_node.children]) == sorted(['int_value', 'str_value'])


_EXPRESSION_TEST_PARAMETERS = [
    ('', None, None),
    (' ', {'some_key': 1}, None),
    ('2 + 2', None, 4),
    ('some_key', {'some_key': 1}, 1),
    ('some_key - 1', {'some_key': 1}, 0),
    ('str(some_key)', {'some_key': 1}, '1'),
    ('some_key', {'some_key': 'asdf'}, 'asdf'),
    ('some_key(some_value)', {'some_key': lambda val: val, 'some_value': 'value'}, 'value')
]


class ExecuteTests:
    @staticmethod
    @mark.parametrize('code, params, expected', _EXPRESSION_TEST_PARAMETERS)
    def test_execute_expression(code, params, expected):
        """execute() should return expression value"""
        expression = Expression(code)

        actual = execute(expression, params)

        assert expected == actual

    @staticmethod
    @mark.parametrize('code, params, expected', _EXPRESSION_TEST_PARAMETERS)
    def test_execute_source_code(code, params, expected):
        """execute() should return expression value"""
        actual = execute(code, params)

        assert expected == actual

    @staticmethod
    @mark.parametrize('expression', [
        '2/0',
        Expression('print(some_variable)')
    ])
    def test_execute_raises(expression):
        """execute() should raise error if expression is invalid"""
        with raises(ExpressionError):
            execute(expression)
