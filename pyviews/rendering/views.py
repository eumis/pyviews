"""View logic"""

from os.path import join

from injectool import resolve

from pyviews.core.error import PyViewsError
from pyviews.core.xml import XmlNode, parse


class ViewError(PyViewsError):
    """Common error for parsing exceptions"""


_XML_CACHE = {}


def get_view_root(view_name: str) -> XmlNode:
    """Parses xml file and return root XmlNode"""
    path = join(resolve('views_folder'), f'{view_name}.{resolve("view_ext")}')
    if path not in _XML_CACHE:
        parse_root(path, view_name)
    return _XML_CACHE[path]


def parse_root(path: str, view_name: str):
    try:
        with open(path, 'rb') as xml_file:
            _XML_CACHE[path] = parse(xml_file, view_name)
    except FileNotFoundError as exc:
        error = ViewError('View is not found')
        error.add_info('View name', view_name)
        error.add_info('Path', path)
        raise error from exc
