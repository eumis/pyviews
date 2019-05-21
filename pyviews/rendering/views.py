"""View logic"""

from os.path import join
from sys import exc_info

from injectool import resolve

from pyviews.core import CoreError, ViewInfo
from pyviews.core.xml import Parser, XmlNode
from pyviews.core import render


class ViewError(CoreError):
    """Common error for parsing exceptions"""


def render_view(view_name, **args):
    """Process view and return root Node"""
    try:
        root_xml = get_view_root(view_name)
        return render(root_xml, **args)
    except CoreError as error:
        error.add_view_info(ViewInfo(view_name, None))
        raise
    except:
        info = exc_info()
        error = ViewError('Unknown error occurred during rendering', ViewInfo(view_name, None))
        error.add_cause(info[1])
        raise error from info[1]


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
    except CoreError as error:
        error.add_view_info(ViewInfo(view_name, None))
        raise
    except:
        info = exc_info()
        error = ViewError('Unknown error occured during parsing xml', ViewInfo(view_name, None))
        error.add_cause(info[1])
        raise error from info[1]
