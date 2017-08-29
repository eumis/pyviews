from unittest import TestCase, main
import pyviews.common.ioc as tested

class TestContainer(TestCase):
    def setUp(self):
        self.container = tested.Container()

    def test_should_store_dependency(self):
        one = object()
        two = object()
        three = object()
        self.container.register('key', lambda: one)
        self.container.register('paramed', lambda: two)
        self.container.register('paramed', lambda: three, 1)

        self.assertEqual(self.container.get('key'), one)
        self.assertEqual(self.container.get('paramed'), two)
        self.assertEqual(self.container.get('paramed', 1), three)

    def test_should_store_last_dependency(self):
        one = object()
        two = object()
        self.container.register('key', lambda: one)
        self.container.register('key', lambda: two)
        self.container.register('paramed', lambda: one, 1)
        self.container.register('paramed', lambda: two, 1)

        self.assertEqual(self.container.get('key'), two)
        self.assertEqual(self.container.get('paramed', 1), two)

    def test_register_raise_for_non_callable(self):
        with self.assertRaises(Exception):
            self.container.register('key', object())

    def test_get_raise_for_not_exis_dependency(self):
        with self.assertRaises(Exception):
            self.container.get('key')
class ContainerMock:
    def __init__(self):
        self.passed_params = None

    def register(self, name, initializer, param=None):
        self.passed_params = (name, initializer, param)

class TestMethods(TestCase):
    def setUp(self):
        tested.CONTAINER = ContainerMock()  

    def tearDown(self):
        tested.CONTAINER = tested.Container()

    def test_register(self):
        one = object()
        name = 'name'
        param = 'param'

        tested.register(name, one, param)

        self.assertEqual(tested.CONTAINER.passed_params, (name, one, param))

    def test_register_value(self):
        one = object()
        name = 'name'
        param = 'param'

        tested.register_value(name, one, param)

        actual = (tested.CONTAINER.passed_params[0],
                  tested.CONTAINER.passed_params[1](),
                  tested.CONTAINER.passed_params[2])
        self.assertEqual(actual, (name, one, param))

class TestInject(TestCase):
    def test_inject(self):
        one = object()
        two = lambda: one
        tested.register_value('one', one)
        tested.register_value('two', two)

        self.assertEqual(self._get_default_injected(), (one, two))
        self.assertEqual(self._get_kwargs_injected(), (one, two))

    @tested.inject('one', 'two')
    def _get_default_injected(self, one=None, two=None):
        return (one, two)

    @tested.inject('one', 'two')
    def _get_kwargs_injected(self, **kwargs):
        return (kwargs['one'], kwargs['two'])

if __name__ == '__main__':
    main()
