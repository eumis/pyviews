'''View logic'''

from os.path import join
from pyviews.core import CoreError
from pyviews.core.ioc import inject
from pyviews.core.xml import Parser
from pyviews.core.node import RenderArgs

class ViewError(CoreError):
    '''Common error for parsing exceptions'''
    def __init__(self, view_name, inner_message=None):
        message = 'There is error in view "' + view_name + '"'
        super().__init__(message, inner_message)

@inject('render')
def render_view(view_name, render=None):
    '''Process view and return root Node'''
    try:
        root_xml = get_view_root(view_name)
        return render(root_xml, RenderArgs(root_xml))
    except CoreError as error:
        raise ViewError(view_name, error.msg) from error

@inject('views_folder')
@inject('view_ext')
def get_view_root(view_name, views_folder=None, view_ext=None):
    '''Parses xml file and return root XmlNode'''
    try:
        path = join(views_folder, view_name + view_ext)
        parser = Parser()
        with open(path, 'rb') as xml_file:
            return parser.parse(xml_file)
    except CoreError as error:
        raise ViewError(view_name, error.msg) from error
