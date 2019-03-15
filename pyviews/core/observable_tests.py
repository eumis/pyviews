#pylint: disable=missing-docstring

from unittest import TestCase
from unittest.mock import Mock, call
from pyviews.testing import case
from .observable import ObservableEntity, InheritedDict

class ObservableEnt(ObservableEntity):
    def __init__(self, private, name, value):
        super().__init__()
        self._private = private
        self.name = name
        self.value = value

    def get_private(self):
        return self._private

class ObservableEntityTests(TestCase):
    def setUp(self):
        self.observable = ObservableEnt('priv', 'some name', 'some value')
        self.callback = Mock()
        self.add_callback = Mock()
        self.add_callback.side_effect = self._add_name_callback

    def _add_name_callback(self, *args):
        self.observable.observe('name', self.callback)

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
        with self.assertRaises(KeyError, msg='ObservableEntity should raise for unknown attribute'):
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

    def test_observe_in_callback(self):
        self.observable.observe('name', self.add_callback)
        self.observable.name = 'new name'

        msg = 'only callbacks registered before assignment should be called'
        self.assertEqual(self.add_callback.call_count, 1, msg=msg)
        msg = 'callbacks registered in another callback shouldn''t be called'
        self.assertEqual(self.callback.call_count, 0, msg=msg)

        self.observable.name = 'another name'
        msg = 'only callbacks registered before assignment should be called'
        self.assertEqual(self.add_callback.call_count, 2, msg=msg)
        msg = 'callbacks registered in another callback should be called'
        self.assertEqual(self.callback.call_count, 1, msg=msg)

class InheritedDictTests(TestCase):
    @staticmethod
    def _create_inh_dict(own, parent):
        inh_dict = InheritedDict(own)
        if parent:
            inh_dict.inherit(parent)
        return inh_dict

    @case({})
    @case({'key': 'value'})
    @case({'key': 'value', 'two': 1})
    def test_dict_source(self, source):
        inh_dict = InheritedDict(source)

        msg = '__init__ should copy values from source dict'
        self.assertDictEqual(inh_dict.to_dictionary(), source, msg)

    @case({}, 'key', 'value')
    @case({'key': 'value'}, 'key', 1)
    @case({'key': 'value', 'two': 1}, 'two', 'new value')
    def test_inherited_dict_source(self, source, key, value):
        source = InheritedDict(source)

        inh_dict = InheritedDict(source)

        msg = '__init__ should inherit from source inherited dict'
        self.assertDictEqual(inh_dict.to_dictionary(), source.to_dictionary(), msg)

        source[key] = value
        self.assertEqual(inh_dict[key], source[key], msg)

    @case({}, 'key', 'value')
    @case({'key': 'value'}, 'key', 1)
    @case({'key': 'value', 'two': 1}, 'two', 'new value')
    def inherit_should_set_parent_dict(self, parent, key, value):
        parent = InheritedDict(parent)
        inh_dict = InheritedDict()

        inh_dict.inherit(parent)

        msg = 'inherit should use passed dict as parent'
        self.assertDictEqual(inh_dict.to_dictionary(), parent.to_dictionary(), msg)

        parent[key] = value
        self.assertEqual(inh_dict[key], parent[key], msg)

    @case(None, {'key': 'value'}, {'key': 'value'})
    @case({}, {'key': 'value'}, {'key': 'value'})
    @case({'key': 'value'}, {}, {'key': 'value'})
    @case({'key': 'value'}, {'key': 'own value'}, {'key': 'own value'})
    @case({'key': 'value', 'one': 1}, {'key': 'own value'}, {'key': 'own value', 'one': 1})
    def test_keys(self, parent, own, result):
        parent = InheritedDict(parent) if parent else None
        inh_dict = self._create_inh_dict(own, parent)

        msg = 'value by key should return own value, if it exists, otherwise value from parent'
        self.assertDictEqual(inh_dict.to_dictionary(), result, msg)

    @case({'key': 'own value'}, 'key')
    def test_remove_key(self, source, key):
        inh_dict = InheritedDict(source)

        inh_dict.remove_key(key)

        msg = 'remove_key should remove own key'
        self.assertFalse(inh_dict.has_key(key), msg)

    @case({'key': 'value'}, {'key': 'own value'}, 'key', 'value')
    def test_remove_key_start_using_parent(self, parent, own, key, value):
        parent = InheritedDict(parent)
        inh_dict = self._create_inh_dict(own, parent)

        inh_dict.remove_key(key)

        msg = 'remove_key should remove own key and use parent'
        self.assertTrue(inh_dict.has_key(key), msg)
        self.assertEqual(inh_dict[key], value, msg)

    @case(None, {}, 'key', False)
    @case({}, {}, 'key', False)
    @case({'key': 'value'}, {}, 'key', True)
    @case({'key': 'value'}, {'key': 'value'}, 'key', True)
    @case(None, {'key': 'value'}, 'key', True)
    @case({}, {'key': 'value'}, 'key', True)
    @case({'key': 'value'}, {}, 'other key', False)
    @case({}, {'key': 'value'}, 'other key', False)
    def test_has_keys(self, parent, source, key, expected):
        parent = InheritedDict(parent) if parent else None
        inh_dict = self._create_inh_dict(source, parent)

        actual = inh_dict.has_key(key)

        msg = 'has_key should return true for existant keys, otherwise false'
        self.assertEqual(actual, expected, msg)

    def test_raises(self):
        inh_dict = InheritedDict()

        with self.assertRaises(KeyError, msg='KeyError should be raised for unknown key'):
            _ = inh_dict['some key']

    def test_notifying_on_change(self):
        inh_dict = InheritedDict()
        callback = Mock()
        key = 'key'

        inh_dict.observe(key, callback)
        inh_dict[key] = 2

        msg = 'change event should be raised if key changed'
        self.assertTrue(callback.called, msg)

    def test_notifying_on_parent_change(self):
        parent = InheritedDict()
        inh_dict = InheritedDict(parent)
        callback = Mock()
        key = 'key'

        inh_dict.observe(key, callback)
        parent[key] = 2

        msg = 'change event should be raised if key changed in parent'
        self.assertTrue(callback.called, msg)

    def test_get_default(self):
        inh_dict = InheritedDict()

        value = inh_dict.get('key')

        msg = 'get should return None by default in case key is not exists'
        self.assertIsNone(value, msg)

    @case(None)
    @case('')
    @case(1)
    @case(True)
    def test_get_passed_default(self, default):
        inh_dict = InheritedDict()

        value = inh_dict.get('key', default)

        msg = 'get should return passed default in case key is not exists'
        self.assertEqual(value, default, msg)

    @case(0)
    @case(1)
    @case(10)
    def test_len_should_return_keys_count(self, count):
        inh_dict = InheritedDict()
        for i in range(count):
            inh_dict[str(i)] = i

        msg = 'len should return keys count'
        self.assertEqual(len(inh_dict), count, msg)

    def test_observe_all(self):
        inherited_dict = InheritedDict()
        callback = Mock()
        inherited_dict.observe_all(callback)

        inherited_dict['name'] = 'new name'
        inherited_dict['value'] = 'new value'

        msg = 'callback should be called on observed property change'
        self.assertTrue(callback.called, msg)
        self.assertEqual(callback.call_count, 2, msg)

        msg = '(new value, old value) args should be passed to self.callback'
        self.assertEqual(callback.call_args_list, [call('name', 'new name', None), call('value', 'new value', None)])

    def test_release_all_callback(self):
        inherited_dict = InheritedDict()
        callback = Mock()
        active_callback = Mock()
        inherited_dict.observe_all(callback)
        inherited_dict.observe_all(active_callback)

        inherited_dict.release_all(callback)
        inherited_dict['name'] = 'new name'
        inherited_dict['value'] = 'new value'

        msg = 'released callbacks shouldn''t be called'
        self.assertTrue(active_callback.called, msg)
        self.assertFalse(callback.called, msg)
