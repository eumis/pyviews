'''View logic'''

from os.path import join
from sys import exc_info
from pyviews.core import CoreError, ViewInfo
from pyviews.core.ioc import SERVICES as deps
from pyviews.core.xml import Parser, XmlNode
from pyviews.container import render

class ViewError(CoreError):
    '''Common error for parsing exceptions'''

def render_view(view_name, **args):
    '''Process view and return root Node'''
    try:
        root_xml = get_view_root(view_name)
        return render(root_xml, **args)
    except CoreError as error:
        error.add_view_info(ViewInfo(view_name, None))
        raise
    except:
        info = exc_info()
        error = ViewError('Unknown error occured during rendering', ViewInfo(view_name, None))
        error.add_cause(info[1])
        raise error from info[1]

_XML_CACHE = {}

def get_view_root(view_name: str) -> XmlNode:
    '''Parses xml file and return root XmlNode'''
    try:
        path = join(deps.views_folder, '{0}.{1}'.format(view_name, deps.view_ext))
        parser = Parser()
        if path not in _XML_CACHE:
            with open(path, 'rb') as xml_file:
                _XML_CACHE[path] = parser.parse(xml_file, view_name)
        return _XML_CACHE[path]
    except FileNotFoundError as error:
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
