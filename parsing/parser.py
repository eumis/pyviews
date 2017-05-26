import xml.etree.ElementTree as ET

def parse_xml(path):
    tree = ET.parse(path)
    return tree.getroot()
   