from injectool import resolve
from pytest import mark

from pyviews.binding import Binder
from pyviews.binding.setup import use_binding


@mark.usefixtures('container_fixture')
class UseBindingTests:
    @staticmethod
    def test_registers_new_binder():
        """should add Binder to container"""
        use_binding()

        assert isinstance(resolve(Binder), Binder)

    @staticmethod
    def test_registers_passed_binder():
        """should add passed Binder to container"""
        binder = Binder()

        use_binding(binder)

        assert resolve(Binder) == binder

    # noinspection PyProtectedMember
    @staticmethod
    def test_adds_bindings():
        """should add bindings to binder"""
        use_binding()

        binder = resolve(Binder)

        assert 'once' in binder._rules
        assert 'oneway' in binder._rules
        assert 'inline' in binder._rules
        assert 'inject' in binder._rules
