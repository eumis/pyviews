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

class TestBinding(TestCase):
    def test_binding_creation(self):
        view_model = InnerViewModel(2, 'inner str')
        expression = Expression('str(vm.int_value) + vm.str_value')
        inst = TestBindable()
        target = BindingTarget(inst, 'str_value', setattr)
        binding = Binding(target, expression)
        vars_ = ExpressionVars()
        vars_['vm'] = view_model
        binding.bind(vars_)

        msg = 'property should be updated on binding creation'
        self.assertEqual(inst.str_value, str(view_model.int_value) + view_model.str_value, msg)

    def test_binding(self):
        view_model = InnerViewModel(2, 'inner str')
        expression = Expression('str(vm.int_value) + vm.str_value')
        inst = TestBindable()
        target = BindingTarget(inst, 'str_value', setattr)
        binding = Binding(target, expression)
        vars_ = ExpressionVars()
        vars_['vm'] = view_model
        binding.bind(vars_)

        msg = 'property should be updated on vm change'

        view_model.int_value = 3
        self.assertEqual(inst.str_value, str(view_model.int_value) + view_model.str_value, msg)

        view_model.str_value = 'new str value'
        self.assertEqual(inst.str_value, str(view_model.int_value) + view_model.str_value, msg)

    def test_destroy(self):
        view_model = InnerViewModel(2, 'inner str')
        expression = Expression('str(vm.int_value) + vm.str_value')
        inst = TestBindable()
        target = BindingTarget(inst, 'str_value', setattr)
        binding = Binding(target, expression)
        expected = inst.str_value
        binding.destroy()

        msg = 'destroy should remove property change on expression change'

        view_model.int_value = 3
        self.assertEqual(inst.str_value, expected, msg)

        view_model.str_value = 'new str value'
        self.assertEqual(inst.str_value, expected, msg)

if __name__ == '__main__':
    main()
