from os.path import join
from pyviews.core.ioc import inject
from pyviews.core.xml import get_root
from pyviews.core.parsing import NodeArgs

@inject('parse')
def parse_view(view_name, parse=None):
    root_xml = get_view_root(view_name)
    return parse(root_xml, NodeArgs(root_xml))

@inject('views_folder')
@inject('view_ext')
def get_view_root(view_name, views_folder=None, view_ext=None):
    path = join(views_folder, view_name + view_ext)
    return get_root(path)
