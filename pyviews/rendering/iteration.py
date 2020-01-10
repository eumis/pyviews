from sys import exc_info
from typing import List, Iterator, Union, NamedTuple

from injectool import dependency, use_container, get_container, add_singleton
from rx import Observable
from rx.core.typing import Observable as GenericObservable, Observer
from rx.subject import Subject

from pyviews.core import Node, ViewsError
from pyviews.rendering.common import RenderingContext, RenderingError
from pyviews.rendering.pipeline import get_pipeline, RenderingPipeline


class RenderingItem(NamedTuple):
    """Tuple with rendering pipeline and rendering context"""
    pipeline: RenderingPipeline
    context: RenderingContext
    subject: Observer


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


def _render_after(ctx: RenderingContext, iterator: RenderingIterator) -> Union[GenericObservable[Node], Observable]:
    obs = Subject()
    iterator.insert([RenderingItem(get_pipeline(ctx.xml_node), ctx, obs)])
    return obs


@dependency
def render(context: RenderingContext) -> Union[GenericObservable[Node], Observable]:
    """Renders node from xml node"""
    try:
        pipeline = get_pipeline(context.xml_node)
        iterator = RenderingIterator()
        node_source = pipeline.run(context)
        with use_container(get_container().copy()):
            add_singleton(render, lambda ctx, it=iterator: _render_after(ctx, it))
            for pipeline, context, observer in iterator:
                pipeline.run(context).subscribe(observer)
        return node_source
    except ViewsError as error:
        error.add_view_info(context.xml_node.view_info)
        raise
    except BaseException:
        info = exc_info()
        msg = 'Unknown error occurred during rendering'
        error = RenderingError(msg, context.xml_node.view_info)
        error.add_cause(info[1])
        raise error from info[1]
