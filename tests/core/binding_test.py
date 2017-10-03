from unittest import TestCase, main
from pyviews.core.binding import Binding, BindingTarget
from pyviews.core.compilation import Expression, ExpressionVars
from pyviews.core.observable import ObservableEnt

class InnerViewModel(ObservableEnt):
    def __init__(self, int_value, str_value):
        super().__init__()
        self.int_value = int_value
        self.str_value = str_value

    def to_string(self):
        return str(self.int_value) + self.str_value

class ParentViewModel(ObservableEnt):
    def __init__(self, int_value, inner_vm):
        super().__init__()
        self.int_value = int_value
        self.inner_vm = inner_vm
        self.another_vm = inner_vm

    def to_string(self):
        return str(self.int_value)

class TestBindable:
    def __init__(self):
        self.int_value = 1
        self.str_value = 'str'

class TestBindingTarget(TestCase):
    def test_set_value(self):
        inst = TestBindable()
        target = BindingTarget(inst, 'int_value', setattr)
        new_val = 25

        target.set_value(new_val)

        msg = 'set_value should return expression result value'
        self.assertEqual(inst.int_value, new_val, msg)

class TestBindingWithSimpleExpression(TestCase):
    def setUp(self):
        self.view_model = InnerViewModel(2, 'inner str')
        self.expression = Expression('str(vm.int_value) + vm.str_value')
        self.inst = TestBindable()
        self.target = BindingTarget(self.inst, 'str_value', setattr)
        self.binding = Binding(self.target, self.expression)
        self.vars = ExpressionVars()
        self.vars['vm'] = self.view_model

    def test_binding_creation(self):
        self.binding.bind(self.vars)

        msg = 'property should be updated on binding creation'
        actual = str(self.view_model.int_value) + self.view_model.str_value
        self.assertEqual(self.inst.str_value, actual, msg)

    def test_binding(self):
        self.binding.bind(self.vars)

        msg = 'property should be updated on vm change'

        self.view_model.int_value = 3
        actual = str(self.view_model.int_value) + self.view_model.str_value
        self.assertEqual(self.inst.str_value, actual, msg)

        self.view_model.str_value = 'new str value'
        actual = str(self.view_model.int_value) + self.view_model.str_value
        self.assertEqual(self.inst.str_value, actual, msg)

    def test_destroy(self):
        expected = self.inst.str_value
        self.binding.destroy()

        msg = 'destroy should remove property change on expression change'

        self.view_model.int_value = 3
        self.assertEqual(self.inst.str_value, expected, msg)

        self.view_model.str_value = 'new str value'
        self.assertEqual(self.inst.str_value, expected, msg)

class TestBindingWithInnerViewModel(TestCase):
    def setUp(self):
        inner_vm = InnerViewModel(2, 'inner str')
        self.view_model = ParentViewModel(3, inner_vm)
        self.expression = Expression('str(vm.int_value) + vm.inner_vm.str_value')
        self.inst = TestBindable()
        self.target = BindingTarget(self.inst, 'str_value', setattr)
        self.binding = Binding(self.target, self.expression)
        self.vars = ExpressionVars()
        self.vars['vm'] = self.view_model

    def test_binding(self):
        self.binding.bind(self.vars)

        msg = 'property should be updated on vm change'
        self.view_model.int_value = 3
        actual = str(self.view_model.int_value) + self.view_model.inner_vm.str_value
        self.assertEqual(self.inst.str_value, actual, msg)

        msg = 'property should be updated on inner vm change'
        self.view_model.inner_vm.str_value = 'new str value'
        actual = str(self.view_model.int_value) + self.view_model.inner_vm.str_value
        self.assertEqual(self.inst.str_value, actual, msg)

        msg = 'property should be updated on inner vm change'
        self.view_model.inner_vm = InnerViewModel(50, 'new inner value')
        actual = str(self.view_model.int_value) + self.view_model.inner_vm.str_value
        self.assertEqual(self.inst.str_value, actual, msg)

        msg = 'property should be updated on inner vm property change'
        self.view_model.inner_vm.str_value = 'new str value'
        actual = str(self.view_model.int_value) + self.view_model.inner_vm.str_value
        self.assertEqual(self.inst.str_value, actual, msg)

if __name__ == '__main__':
    main()
