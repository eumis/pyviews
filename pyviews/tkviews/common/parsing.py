import xml.etree.ElementTree as ET
from os.path import join
from pyviews.common.ioc import inject

@inject('views_folder', 'view_ext')
def parse_xml(view, views_folder='views', view_ext='.xml'):
    view_path = join(views_folder, view + view_ext)
    return ET.parse(view_path).getroot()

def has_namespace(name):
    return name.startswith('{') and '}' in name

def parse_namespace(name):
    if not has_namespace(name):
        raise ParsingException("Name " + name + "doesn't contain namespace")
    splitted = name.split('}', maxsplit=1)
    namespace = splitted[0][1:]
    name = splitted[1]
    return (namespace, name)

class ParsingException(Exception):
    pass
