from unittest.mock import Mock

from pytest import fixture, mark

from pyviews.binding.twoways import TwoWaysBinding


@fixture
def two_ways_fixture(request):
    one, two = Mock(), Mock()
    binding = TwoWaysBinding(one, two)

    request.cls.one = one
    request.cls.two = two
    request.cls.binding = binding


@mark.usefixtures('two_ways_fixture')
class TwoWaysBindingTests:
    """TwoWaysBinding tests using ExpressionBinding and ObservableBinding"""

    binding: TwoWaysBinding
    one: Mock
    two: Mock

    def test_bind(self):
        """should bind both bindings"""
        self.binding.bind()

        assert self.one.bind.called and self.two.bind.called

    def test_destroy(self):
        """should bind both bindings"""
        self.binding.destroy()

        assert self.one.destroy.called and self.two.destroy.called
