'''View logic'''

from os.path import join
from sys import exc_info

from pyviews.core import CoreError, ViewInfo
from pyviews.core.ioc import inject
from pyviews.core.node import RenderArgs
from pyviews.core.xml import Parser, XmlNode

class ViewError(CoreError):
    '''Common error for parsing exceptions'''
    pass

@inject('render')
def render_view(view_name, render=None):
    '''Process view and return root Node'''
    try:
        root_xml = get_view_root(view_name)
        return render(root_xml, RenderArgs(root_xml))
    except CoreError as error:
        error.add_view_info(ViewInfo(view_name, None))
        raise
    except:
        info = exc_info()
        error = ViewError('Unknown error occured during rendering', ViewInfo(view_name, None))
        error.add_cause(info[1])
        raise error from info[1]

_XML_CACHE = {}

@inject('views_folder')
@inject('view_ext', 'views_folder')
def get_view_root(view_name: str, views_folder: str = None, view_ext: str = None) -> XmlNode:
    '''Parses xml file and return root XmlNode'''
    try:
        path = join(views_folder, '{0}.{1}'.format(view_name, view_ext))
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
