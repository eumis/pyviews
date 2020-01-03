from sys import exc_info
from typing import List, Iterator

from injectool import dependency

from pyviews.core import Node, ViewsError
from pyviews.rendering.common import RenderingContext, RenderingError
from pyviews.rendering.pipeline import RenderingItem
from pyviews.rendering.pipeline import get_pipeline


class RenderingIterator:
    def __init__(self, root: RenderingItem = None):
        self._items: List[RenderingItem] = [root] if root else []
        self._index = 0

    def __iter__(self) -> Iterator[RenderingItem]:
        return self

    def __next__(self) -> RenderingItem:
        try:
            self._index += 1
            return self._items[self._index - 1]
        except IndexError:
            raise StopIteration()

    def insert(self, items: List[RenderingItem]):
        """Inserts items to iterator"""
        self._items = self._items[:self._index] + items + self._items[self._index:]


@dependency
def render(context: RenderingContext) -> Node:
    """Renders node from xml node"""
    try:
        pipeline = get_pipeline(context.xml_node)
        iterator = RenderingIterator()
        node = pipeline.run(context, iterator.insert)
        for pipeline, context in iterator:
            pipeline.run(context, iterator.insert)
        return node
    except ViewsError as error:
        error.add_view_info(context.xml_node.view_info)
        raise
    except BaseException:
        info = exc_info()
        msg = 'Unknown error occurred during rendering'
        error = RenderingError(msg, context.xml_node.view_info)
        error.add_cause(info[1])
        raise error from info[1]
