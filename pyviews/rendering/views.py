"""View logic"""

from os.path import join

from injectool import resolve, dependency

from pyviews.core import PyViewsError, ViewInfo, Node
from pyviews.core.xml import Parser, XmlNode
from .common import RenderingContext
from .pipeline import render
from ..core.error import error_handling


class ViewError(PyViewsError):
    """Common error for parsing exceptions"""


@dependency
def render_view(view_name: str, context: RenderingContext) -> Node:
    """Renders view"""
    with error_handling(ViewError,
                        lambda e: e.add_view_info(ViewInfo(view_name, None))):
        context.xml_node = get_view_root(view_name)
        return render(context)


_XML_CACHE = {}


def get_view_root(view_name: str) -> XmlNode:
    """Parses xml file and return root XmlNode"""
    path = join(resolve('views_folder'), '{0}.{1}'.format(view_name, resolve('view_ext')))
    if path not in _XML_CACHE:
        _parse_root(path, view_name)
    return _XML_CACHE[path]


def _parse_root(path, view_name):
    try:
        parser = Parser()
        with open(path, 'rb') as xml_file:
            _XML_CACHE[path] = parser.parse(xml_file, view_name)
    except FileNotFoundError:
        error = ViewError('View is not found')
        error.add_info('View name', view_name)
        error.add_info('Path', path)
        raise error
