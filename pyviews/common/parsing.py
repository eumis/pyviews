import xml.etree.ElementTree as ET
from os.path import join
from pyviews.common import settings

def parse_xml(view):
    view_path = join(settings.VIEWS_FOLDER, view + settings.VIEW_EXT)
    return ET.parse(view_path).getroot()
