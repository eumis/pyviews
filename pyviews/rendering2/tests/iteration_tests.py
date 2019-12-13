from unittest.mock import Mock

from pytest import fixture, mark, raises

from pyviews.rendering2.iteration import RenderingIterator


@fixture
def rendering_iterator_fixture(request):
    root = Mock()
    iterator = RenderingIterator(root)

    request.cls.root = root
    request.cls.iterator = iterator


@mark.usefixtures('rendering_iterator_fixture')
class RenderingIteratorTests:
    def test_uses_root(self):
        actual = next(self.iterator)

        assert actual == self.root

    def test_raises_stop_iteration(self):
        next(self.iterator)

        with raises(StopIteration):
            next(self.iterator)

    @mark.parametrize('items', [
        [Mock()],
        [Mock(), Mock()],
        [Mock(), Mock(), Mock()]
    ])
    def test_inserts_adds_items(self, items):
        next(self.iterator)

        self.iterator.insert(items)

        actual = list(self.iterator)
        assert actual == items

    @mark.parametrize('items', [
        [Mock()],
        [Mock(), Mock()],
        [Mock(), Mock(), Mock()]
    ])
    def test_inserts_after_current(self, items):
        self.iterator.insert(items)

        actual = list(self.iterator)
        assert actual == items + [self.root]
