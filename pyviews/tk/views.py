from os.path import join
from pyviews.core.ioc import inject
from pyviews.core.xml import get_root
from pyviews.core.parsing import NodeArgs

@inject('views_folder')
@inject('parse')
@inject('view_ext')
def parse_view(view_name, views_folder=None, parse=None, view_ext=None):
    path = join(views_folder, view_name + view_ext)
    root_xml = get_root(path)
    return parse(root_xml, NodeArgs(root_xml))
