from unittest import TestCase, main
from unittest.mock import Mock, call
from pyviews.core.observable import ObservableEnt

class ObservableEntity(ObservableEnt):
    def __init__(self, private, name, value):
        super().__init__()
        self._private = private
        self.name = name
        self.value = value

    def get_private(self):
        return self._private

class TestObservableCallback(TestCase):
    def setUp(self):
        self.observable = ObservableEntity('priv', 'some name', 'some value')
        self.callback = Mock()

    def test_observe(self):
        self.observable.observe('name', self.callback)

        self.observable.name = 'new name'
        self.observable.value = 'new value'

        msg = 'self.callback should be called on observed property change'
        self.assertTrue(self.callback.called, msg)
        self.assertEqual(self.callback.call_count, 1, msg)

        msg = '(new value, old value) args should be passed to self.callback'
        self.assertEqual(self.callback.call_args, call('new name', 'some name'), msg)

    def test_observe_raises(self):
        with self.assertRaises(KeyError, msg='ObservableEnt should raise for unknown attribute'):
            self.observable.observe('attr', lambda: self.callback)

    def test_release_callback(self):
        self.observable.observe('name', self.callback)
        self.observable.observe('value', self.callback)

        self.observable.release('name', self.callback)
        self.observable.name = 'new name'
        self.observable.value = 'new value'

        msg = 'self.callback should be called on observed property change'
        self.assertTrue(self.callback.called, msg)

        msg = 'self.callback shouldn''t be called after realeasing'
        self.assertEqual(self.callback.call_count, 1, msg)

        msg = 'self.callback should be called only for observed properties'
        self.assertEqual(self.callback.call_args, call('new value', 'some value'), msg)

# class TestDictionary(TestCase):
#     def test_observe(self):
#         dictionary = ObservableDict()
#         self.callback = Mock()

#         dictionary.observe(self.callback)
#         dictionary['one'] = 1
#         dictionary['two'] = 'two'
#         dictionary['one'] = 'one'

#         msg = 'self.callback should be called once for every change'
#         self.assertEqual(self.callback.call_count, 3, msg)

#         msg = 'self.callback should be called with new and old value as parameters'
#         self.assertEqual(self.callback.call_args_list[0], call('one', 1, None), msg)
#         self.assertEqual(self.callback.call_args_list[1], call('two', 'two', None), msg)
#         self.assertEqual(self.callback.call_args_list[2], call('one', 'one', 1), msg)

#     def test_observe_once(self):
#         dictionary = ObservableDict()
#         self.callback = Mock()

#         dictionary.observe(self.callback)
#         dictionary.observe(self.callback)
#         dictionary['one'] = 1

#         msg = 'self.callback should be registered once'
#         self.assertEqual(self.callback.call_count, 1, msg)

#     def test_release(self):
#         dictionary = ObservableDict()
#         self.callback = Mock()

#         dictionary.observe(self.callback)
#         dictionary['one'] = 1
#         dictionary.release(self.callback)
#         dictionary['two'] = 'two'

#         msg = 'self.callback shouldn''t be called after releasing'
#         self.assertEqual(self.callback.call_count, 1, msg)

if __name__ == '__main__':
    main()
