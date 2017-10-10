import xml.etree.ElementTree as ET

class XmlNode:
    def __init__(self, element: ET.Element):
        self._element = element
        (self.module_name, self.class_name) = parse_namespace(element.tag)
        self.text = '' if element.text is None else element.text.strip()

    @property
    def class_path(self):
        return self.module_name + '.' + self.class_name

    def get_children(self):
        return [XmlNode(el) for el in list(self._element)]

    def get_attrs(self):
        return [XmlAttr(attr) for attr in self._element.items()]

class XmlAttr:
    def __init__(self, attr):
        (self.name, self.value) = attr
        self.namespace = None
        if has_namespace(self.name):
            (self.namespace, self.name) = parse_namespace(self.name)

def has_namespace(name):
    return name.startswith('{') and '}' in name

def parse_namespace(name):
    if not has_namespace(name):
        raise ParsingError("Name " + name + "doesn't contain namespace")
    splitted = name.split('}', maxsplit=1)
    namespace = splitted[0][1:]
    name = splitted[1]
    return (namespace, name)

class ParsingError(Exception):
    pass

def get_root(xml_path):
    try:
        root_element = ET.parse(xml_path).getroot()
        return XmlNode(root_element)
    except ET.ParseError as error:
        raise ParsingError(error)
