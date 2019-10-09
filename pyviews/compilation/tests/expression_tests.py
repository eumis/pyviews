from pytest import mark, raises, fixture

from pyviews.core import CompilationError
from pyviews.compilation.expression import CompiledExpression


@fixture
def object_tree_fixture(request):
    expression = CompiledExpression("str(vm.vm.int_value) + vm.vm.str_value + vm.str_value + vm.get()")
    root = expression.get_object_tree()
    str_node = [entry for entry in root.children if entry.key == 'str'][0]
    vm_node = [entry for entry in root.children if entry.key == 'vm'][0]
    vm_node_str = [entry for entry in vm_node.children if entry.key == 'str_value'][0]
    vm_node_vm = [entry for entry in vm_node.children if entry.key == 'vm'][0]

    request.cls.expression = expression
    request.cls.root = root
    request.cls.str_node = str_node
    request.cls.vm_node = vm_node
    request.cls.vm_node_str = vm_node_str
    request.cls.vm_node_vm = vm_node_vm


@mark.usefixtures('object_tree_fixture')
class EvalExpressionTests:

    @staticmethod
    @mark.parametrize('code, params, expected', [
        ('', None, None),
        (' ', {'some_key': 1}, None),
        ('2 + 2', None, 4),
        ('some_key', {'some_key': 1}, 1),
        ('some_key - 1', {'some_key': 1}, 0),
        ('str(some_key)', {'some_key': 1}, '1'),
        ('some_key', {'some_key': 'asdf'}, 'asdf'),
        ('some_key(some_value)', {'some_key': lambda val: val, 'some_value': 'value'}, 'value')
    ])
    def test_execute(code, params, expected):
        """execute() should return expression value"""
        expression = CompiledExpression(code)

        actual = expression.execute(params)

        assert expected == actual

    @staticmethod
    @mark.parametrize('body', [
        '2/0',
        'print(some_variable)'
    ])
    def test_execute_raises(body):
        """execute() should raise error if expression is invalid"""
        expression = CompiledExpression(body)

        with raises(CompilationError):
            expression.execute()

    def test_root(self):
        """get_object_tree() should return objects tree root"""
        assert self.root.key == 'root'

    def test_locals(self):
        """get_object_tree(): root should contain local variables"""
        assert sorted([e.key for e in self.root.children]) == sorted(['str', 'vm'])

    def test_method(self):
        """get_object_tree(): method node should not contain any child"""
        assert [e.key for e in self.str_node.children] == []

    def test_property(self):
        """get_object_tree(): object node should have children node for property"""
        assert sorted([e.key for e in self.vm_node.children]) == sorted(['vm', 'str_value', 'get'])

    def test_empty_children(self):
        """get_object_tree(): object node should not have children if there are not properties used in expression"""
        assert [e.key for e in self.vm_node_str.children] == []

    def test_property_children(self):
        """get_object_tree(): object node should have children if there are its properties used in expression"""
        assert sorted([e.key for e in self.vm_node_vm.children]) == sorted(['int_value', 'str_value'])
