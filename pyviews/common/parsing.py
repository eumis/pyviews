import xml.etree.ElementTree as ET
from os.path import join
from pyviews.common import settings

def parse_xml(view):
    view_path = join(settings.VIEWS_FOLDER, view + settings.VIEW_EXT)
    return ET.parse(view_path).getroot()

def has_namespace(name):
    return name.startswith('{')

def parse_namespace(name):
    splitted = name.split('}', maxsplit=1)
    name_space = splitted[0][1:]
    name = splitted[1]
    return (name_space, name)
