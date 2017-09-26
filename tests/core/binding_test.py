from unittest import TestCase, main
from tests.utility import case
from pyviews.core.binding import PropertyGetRecorder, Binding
from pyviews.core.compilation import Expression
from pyviews.core.observable import Observable

class InnerViewModel(Observable):
    def __init__(self, int_value, str_value):
        super().__init__()
        self.int_value = int_value
        self.str_value = str_value

class ParentViewModel(Observable):
    def __init__(self, int_value, inner_vm):
        super().__init__()
        self.int_value = int_value
        self.inner_vm = inner_vm
        self.another_vm = inner_vm

class TestPropertyGetRecorder(TestCase):
    def setUp(self):
        self.inner_vm = InnerViewModel(1, 'str_value')
        self.view_model = ParentViewModel(1, self.inner_vm)
        self.recorder = PropertyGetRecorder(self.view_model)

    def test_properties(self):
        msg = 'recorder should return values from vm'
        self.assertEqual(self.recorder.int_value, self.view_model.int_value, msg)
        self.assertEqual(self.recorder.inner_vm.int_value, self.view_model.inner_vm.int_value, msg)
        self.assertEqual(self.recorder.inner_vm.str_value, self.view_model.inner_vm.str_value, msg)

    def test_inner_vm(self):
        msg = 'recorder should replace inner ViewModel by recorder'
        self.assertIsInstance(self.recorder.inner_vm, PropertyGetRecorder, msg)

    def test_get_used_properties(self):
        self.recorder.int_value
        self.recorder.inner_vm.str_value

        used_properties = self.recorder.get_used_properties()

        msg = 'view models with called properties should be returned'
        self.assertTrue(self.view_model in used_properties, msg)
        self.assertTrue(self.inner_vm in used_properties, msg)

        msg = 'called properties should be returned'
        self.assertTrue('int_value' in used_properties[self.view_model], msg)
        self.assertTrue('inner_vm' in used_properties[self.view_model], msg)
        self.assertTrue('str_value' in used_properties[self.inner_vm], msg)

    def test_properties_duplicates(self):
        self.recorder.int_value
        self.recorder.int_value
        self.recorder.inner_vm
        self.recorder.inner_vm

        used_properties = self.recorder.get_used_properties()

        msg = 'only view models with called properties should be returned'
        self.assertEqual(len(used_properties), 1, msg)
        self.assertTrue('inner_vm' in used_properties[self.view_model], msg)

        msg = 'only called properties should be returned'
        self.assertEqual(len(used_properties[self.view_model]), 2, msg)
        self.assertTrue('int_value' in used_properties[self.view_model], msg)
        self.assertTrue('inner_vm' in used_properties[self.view_model], msg)

class TestBindable:
    def __init__(self):
        self.int_value = 1
        self.str_value = 'str'

class TestBinding(TestCase):
    @case('2 + 2', None, 4)
    @case('some_key', {'some_key': 1}, 1)
    @case('some_key - 1', {'some_key': 1}, 0)
    @case('str(some_key)', {'some_key': 1}, '1')
    @case('some_key', {'some_key': 'asdf'}, 'asdf')
    @case('some_key(some_value)', {'some_key': lambda val: val, 'some_value': 'value'}, 'value')
    def test_get_value(self, code, params, expected):
        expression = Expression(code, params)
        inst = TestBindable()
        binding = Binding(inst, 'int_value', setattr, expression)

        msg = 'get_value should return expression result value'
        self.assertEqual(binding.get_value(), expected, msg)

    def test_get_value_parameters(self):
        expression = Expression('(one, two)', {'one': 1, 'two': 2})
        inst = TestBindable()
        binding = Binding(inst, 'int_value', setattr, expression)

        msg = 'get_value should return expression result value'
        expected = ('one value', 'two value')
        self.assertEqual(binding.get_value({'one': 'one value', 'two': 'two value'}), expected, msg)

    def test_update_prop(self):
        view_model = InnerViewModel(2, 'inner str')
        expression = Expression('str(vm.int_value) + vm.str_value', {'vm': view_model})
        inst = TestBindable()
        binding = Binding(inst, 'str_value', setattr, expression)

        binding.update_prop()

        msg = 'update_prop should compile expression and set result to binded property'
        self.assertEqual(inst.str_value, str(view_model.int_value) + view_model.str_value, msg)

    def test_binding_creation(self):
        view_model = InnerViewModel(2, 'inner str')
        expression = Expression('str(vm.int_value) + vm.str_value', {'vm': view_model})
        inst = TestBindable()
        Binding(inst, 'str_value', setattr, expression)

        msg = 'property should be updated on binding creation'
        self.assertEqual(inst.str_value, str(view_model.int_value) + view_model.str_value, msg)

    def test_binding(self):
        view_model = InnerViewModel(2, 'inner str')
        expression = Expression('str(vm.int_value) + vm.str_value', {'vm': view_model})
        inst = TestBindable()
        Binding(inst, 'str_value', setattr, expression)

        msg = 'property should be updated on vm change'

        view_model.int_value = 3
        self.assertEqual(inst.str_value, str(view_model.int_value) + view_model.str_value, msg)

        view_model.str_value = 'new str value'
        self.assertEqual(inst.str_value, str(view_model.int_value) + view_model.str_value, msg)

    def test_destroy(self):
        view_model = InnerViewModel(2, 'inner str')
        expression = Expression('str(vm.int_value) + vm.str_value', {'vm': view_model})
        inst = TestBindable()
        binding = Binding(inst, 'str_value', setattr, expression)
        expected = inst.str_value
        binding.destroy()

        msg = 'destroy should remove property change on expression change'

        view_model.int_value = 3
        self.assertEqual(inst.str_value, expected, msg)

        view_model.str_value = 'new str value'
        self.assertEqual(inst.str_value, expected, msg)

if __name__ == '__main__':
    main()
