from unittest.mock import Mock, call

from pytest import fixture, raises, mark

from pyviews.core.bindable import BindableEntity, InheritedDict


class TestBindable(BindableEntity):
    def __init__(self, private, name, value):
        super().__init__()
        self._private = private
        self.name = name
        self.value = value

    def get_private(self):
        return self._private


@fixture
def observable_fixture(request):
    request.cls.observable = TestBindable('private', 'some name', 'some value')
    request.cls.callback = Mock()
    request.cls.add_callback = Mock()


@mark.usefixtures('observable_fixture')
class BindableEntityTests:
    """BindableEntity class tests"""

    observable: TestBindable
    callback: Mock
    add_callback: Mock

    def test_observe(self):
        """observe() should subscribe passed callback to property changes"""
        self.observable.observe('name', self.callback)

        self.observable.name = 'new name'
        self.observable.value = 'new value'

        assert self.callback.call_count == 1
        assert self.callback.call_args == call('new name', 'some name')

    def test_observe_raises(self):
        """observe() should raise if entity doesn't have passed property"""
        with raises(KeyError):
            self.observable.observe('attr', lambda: self.callback)

    def test_release_callback(self):
        """release() should unsubscribe callback from property changes"""
        new_name = "new name"
        old_value, new_value = self.observable.value, "new value"
        self.observable.observe('name', self.callback)
        self.observable.observe('value', self.callback)

        self.observable.release('name', self.callback)
        self.observable.name = new_name
        self.observable.value = new_value

        assert self.callback.call_count == 1
        assert self.callback.call_args == call(new_value, old_value)

    def test_release_callback_releases_same_callbacks(self):
        """release() should unsubscribe same callbacks from property changes"""
        new_name = "new name"
        self.observable.observe('name', self.callback)
        self.observable.observe('name', self.callback)

        self.observable.release('name', self.callback)
        self.observable.name = new_name

        assert not self.callback.called

    def test_observe_in_callback(self):
        """observe() inside callback should add new callback"""
        self.observable.observe('name', lambda *args: self.observable.observe('name', self.callback))

        self.observable.name = 'new name'
        assert self.callback.call_count == 0

        self.observable.name = 'another name'
        assert self.callback.call_count == 1


class InheritedDictTests:
    @staticmethod
    def _create_inh_dict(own, parent):
        inh_dict = InheritedDict(own)
        if parent:
            inh_dict.inherit(parent)
        return inh_dict

    @staticmethod
    @mark.parametrize('source', [
        {},
        {'key': 'value'},
        {'key': 'value', 'two': 1},
    ])
    def test_dict_source(source):
        """__init__() should copy values from source dict"""
        inh_dict = InheritedDict(source)

        assert inh_dict.to_dictionary() == source

    @staticmethod
    @mark.parametrize('parent_source, key, new_parent_value', [
        ({}, 'key', 'value'),
        ({'key': 'value'}, 'key', 1),
        ({'key': 'value', 'two': 1}, 'two', 'new value'),
    ])
    def test_inherited_dict_source(parent_source, key, new_parent_value):
        """__init__() should inherit source InheritedDict"""
        parent = InheritedDict(parent_source)
        inh_dict = InheritedDict(parent)

        parent_source[key] = new_parent_value
        assert inh_dict.to_dictionary() == parent.to_dictionary()

    @staticmethod
    @mark.parametrize('parent_source', [
        {},
        {'key': 'value'},
        {'key': 'value', 'two': 1}
    ])
    def test_inheritance(parent_source):
        """inherit() should use parent as source"""
        parent = InheritedDict(parent_source)
        inh_dict = InheritedDict()

        inh_dict.inherit(parent)

        assert inh_dict.to_dictionary() == parent.to_dictionary()

    @staticmethod
    @mark.parametrize('parent_source, key, new_parent_value', [
        ({}, 'key', 'value'),
        ({'key': 'value'}, 'key', 1),
        ({'key': 'value', 'two': 1}, 'two', 'new value'),
    ])
    def test_using_parent_values(parent_source, key, new_parent_value):
        """inherit() should subscribe to parent changes"""
        parent = InheritedDict(parent_source)
        inh_dict = InheritedDict()

        inh_dict.inherit(parent)

        parent[key] = new_parent_value
        assert inh_dict[key] == parent[key]

    @mark.parametrize('parent, own, result', [
        (None, {'key': 'value'}, {'key': 'value'}),
        ({}, {'key': 'value'}, {'key': 'value'}),
        ({'key': 'value'}, {}, {'key': 'value'}),
        ({'key': 'value'}, {'key': 'own value'}, {'key': 'own value'}),
        ({'key': 'value', 'one': 1}, {'key': 'own value'}, {'key': 'own value', 'one': 1})
    ])
    def test_to_dictionary(self, parent, own, result):
        """to_dictionary() should return dict with own values then parent values"""
        parent = InheritedDict(parent) if parent else None
        inh_dict = self._create_inh_dict(own, parent)

        assert inh_dict.to_dictionary() == result

    @staticmethod
    @mark.parametrize('source, key', [
        ({'key': 'own value'}, 'key')
    ])
    def test_remove_key(source, key):
        """remove_key() should remove own key"""
        inh_dict = InheritedDict(source)

        inh_dict.remove_key(key)

        assert key not in inh_dict

    @mark.parametrize('parent, own, key, value', [
        ({'key': 'value'}, {'key': 'own value'}, 'key', 'value')
    ])
    def test_remove_key_start_using_parent(self, parent, own, key, value):
        """remove_key() should start using parent value"""
        parent = InheritedDict(parent)
        inh_dict = self._create_inh_dict(own, parent)

        inh_dict.remove_key(key)

        assert key in inh_dict
        assert inh_dict[key] == value

    @mark.parametrize('parent, source, key, expected', [
        (None, {}, 'key', False),
        ({}, {}, 'key', False),
        ({'key': 'value'}, {}, 'key', True),
        ({'key': 'value'}, {'key': 'value'}, 'key', True),
        (None, {'key': 'value'}, 'key', True),
        ({}, {'key': 'value'}, 'key', True),
        ({'key': 'value'}, {}, 'other key', False),
        ({}, {'key': 'value'}, 'other key', False)
    ])
    def test_key_check(self, parent, source, key, expected):
        """__contains__() should return true if own or parent key exist"""
        parent = InheritedDict(parent) if parent else None
        inh_dict = self._create_inh_dict(source, parent)

        assert (key in inh_dict) == expected

    @staticmethod
    def test_raises():
        """__getitem__() should raise KeyError if key does not exist"""
        inh_dict = InheritedDict()

        with raises(KeyError):
            _ = inh_dict['some key']

    @staticmethod
    def test_notifying_on_change():
        """__setitem__() should notify subscribers"""
        inh_dict = InheritedDict()
        callback = Mock()
        key = 'key'

        inh_dict.observe(key, callback)
        inh_dict[key] = 2

        assert callback.called

    @staticmethod
    def test_notifying_on_parent_change():
        """__setitem__() should notify child subscribers"""
        parent = InheritedDict()
        inh_dict = InheritedDict(parent)
        callback = Mock()
        key = 'key'

        inh_dict.observe(key, callback)
        parent[key] = 2

        assert callback.called

    @staticmethod
    @mark.parametrize('default', [None, '', 1, True])
    def test_get(default):
        """get() should return default if key doesn't exist"""
        inh_dict = InheritedDict()

        value = inh_dict.get('key', default)

        assert value == default

    @staticmethod
    @mark.parametrize('source, parent_source, expected', [
        ({}, None, 0),
        ({'k': 1}, None, 1),
        ({'k': 1, 'a': 'v'}, None, 2),
        ({}, {'k': 1}, 1),
        ({}, {'k': 1, 'a': 'v'}, 2),
        ({'k': 1}, {'a': 'v'}, 2),
        ({'k': 1}, {'k': 'v'}, 1),
        ({'k': 1, 'a': 'v'}, {'k': 2}, 2),
        ({'k': 1, 'a': 'v'}, {'z': 2}, 3)
    ])
    def test_length(source, parent_source, expected):
        """__len__() should return keys count"""
        inh_dict = InheritedDict(source)
        if parent_source is not None:
            inh_dict.inherit(InheritedDict(parent_source))

        assert len(inh_dict) == expected

    @staticmethod
    def test_observe_all():
        """observe_all() should subscribe callback to all existing values changes and new values adding"""
        inherited_dict = InheritedDict()
        callback = Mock()
        inherited_dict.observe_all(callback)

        inherited_dict['name'] = 'new name'
        inherited_dict['value'] = 'new value'

        assert callback.call_args_list == [call('name', 'new name', None), call('value', 'new value', None)]

    @staticmethod
    def test_release_all():
        """release_all() should remove callback subscription to all changes"""
        inherited_dict = InheritedDict()
        callback = Mock()
        active_callback = Mock()
        inherited_dict.observe_all(callback)
        inherited_dict.observe_all(active_callback)

        inherited_dict.release_all(callback)
        inherited_dict['name'] = 'new name'
        inherited_dict['value'] = 'new value'

        assert active_callback.called
        assert not callback.called

    @staticmethod
    def test_release_all_same_callback():
        """release_all() should remove callback subscription to all changes"""
        inherited_dict = InheritedDict()
        callback = Mock()
        inherited_dict.observe_all(callback)
        inherited_dict.observe_all(callback)

        inherited_dict.release_all(callback)
        inherited_dict['name'] = 'new name'
        inherited_dict['value'] = 'new value'

        assert not callback.called
