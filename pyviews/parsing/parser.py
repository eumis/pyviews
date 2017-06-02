import xml.etree.ElementTree as ET

def parse_xml(path):
    return ET.parse(path).getroot()
