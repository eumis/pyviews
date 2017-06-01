import re
import xml.etree.ElementTree as ET

ROOT_REGEX = r'(\<\?.*\?\>\s*){0,1}(\<[\S]*\s)'
ROOT_PLUS_IMPORT_REGEX = r'\2 xmlns:import="import" '

def parse_xml(path):
    xml = ''
    with open(path, 'r') as xml_file:
        xml = xml_file.read()
    xml = add_import_namespace(xml)
    return ET.fromstring(xml)

def add_import_namespace(xml):
    return re.sub(ROOT_REGEX, ROOT_PLUS_IMPORT_REGEX, xml, 1)
