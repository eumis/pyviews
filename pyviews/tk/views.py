from os.path import join
from pyviews.core import CoreError
from pyviews.core.ioc import inject
from pyviews.core.xml import get_root
from pyviews.core.node import NodeArgs

class ViewError(CoreError):
    def __init__(self, view_name, inner_message=None):
        message = 'There is error in view "' + view_name + '"'
        super().__init__(message, inner_message)

@inject('parse')
def parse_view(view_name, parse=None):
    try:
        root_xml = get_view_root(view_name)
        return parse(root_xml, NodeArgs(root_xml))
    except CoreError as error:
        raise ViewError(view_name, error.msg) from error

@inject('views_folder')
@inject('view_ext')
def get_view_root(view_name, views_folder=None, view_ext=None):
    try:
        path = join(views_folder, view_name + view_ext)
        return get_root(path)
    except CoreError as error:
        raise ViewError(view_name, error.msg) from error
