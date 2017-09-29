from unittest import TestCase, main
from unittest.mock import Mock, call
from tests.mock import TestViewModel as ViewModel

class TestViewModel(TestCase):
    def test_get_observable_keys(self):
        view_model = ViewModel('priv', 'some name', 'some value')
        keys = view_model.get_observable_keys()

        msg = 'ViewModel should use public properties as observable'
        expected_keys = [
            'name', 'value', 'observe',
            'release', 'get_observable_keys', 'get_private']
        self.assertListEqual(sorted(keys), sorted(expected_keys), msg)

    def test_observe(self):
        view_model = ViewModel('priv', 'some name', 'some value')
        callback = Mock()
        callback.call_args_list
        view_model.observe('name', callback)

        view_model.name = 'new name'
        view_model.value = 'new value'

        msg = 'callback should be called on observed property change'
        self.assertTrue(callback.called, msg)
        self.assertEqual(callback.call_count, 1, msg)

        msg = '(new value, old value) args should be passed to callback'
        self.assertEqual(callback.call_args, call('new name', 'some name'), msg)

    def test_release_callback(self):
        view_model = ViewModel('priv', 'some name', 'some value')
        callback = Mock()
        view_model.observe('name', callback)
        view_model.observe('value', callback)

        view_model.release('name', callback)
        view_model.name = 'new name'
        view_model.value = 'new value'

        msg = 'callback should be called on observed property change'
        self.assertTrue(callback.called, msg)

        msg = 'callback shouldn''t be called after realeasing'
        self.assertEqual(callback.call_count, 1, msg)

        msg = 'callback should be called only for observed properties'
        self.assertEqual(callback.call_args, call('new value', 'some value'), msg)

# class TestDictionary(TestCase):
#     def test_observe(self):
#         dictionary = ObservableDict()
#         callback = Mock()

#         dictionary.observe(callback)
#         dictionary['one'] = 1
#         dictionary['two'] = 'two'
#         dictionary['one'] = 'one'

#         msg = 'callback should be called once for every change'
#         self.assertEqual(callback.call_count, 3, msg)

#         msg = 'callback should be called with new and old value as parameters'
#         self.assertEqual(callback.call_args_list[0], call('one', 1, None), msg)
#         self.assertEqual(callback.call_args_list[1], call('two', 'two', None), msg)
#         self.assertEqual(callback.call_args_list[2], call('one', 'one', 1), msg)

#     def test_observe_once(self):
#         dictionary = ObservableDict()
#         callback = Mock()

#         dictionary.observe(callback)
#         dictionary.observe(callback)
#         dictionary['one'] = 1

#         msg = 'callback should be registered once'
#         self.assertEqual(callback.call_count, 1, msg)

#     def test_release(self):
#         dictionary = ObservableDict()
#         callback = Mock()

#         dictionary.observe(callback)
#         dictionary['one'] = 1
#         dictionary.release(callback)
#         dictionary['two'] = 'two'

#         msg = 'callback shouldn''t be called after releasing'
#         self.assertEqual(callback.call_count, 1, msg)

if __name__ == '__main__':
    main()
