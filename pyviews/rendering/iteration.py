from sys import exc_info

from injectool import dependency

from pyviews.core import Node, ViewsError
from pyviews.rendering.common import RenderingContext, RenderingError
from pyviews.rendering.pipeline import get_pipeline


@dependency
def render(context: RenderingContext) -> Node:
    """Renders node from xml node"""
    try:
        pipeline = get_pipeline(context.xml_node)
        return pipeline.run(context)
    except ViewsError as error:
        error.add_view_info(context.xml_node.view_info)
        raise
    except BaseException:
        info = exc_info()
        msg = 'Unknown error occurred during rendering'
        error = RenderingError(msg, context.xml_node.view_info)
        error.add_cause(info[1])
        raise error from info[1]
