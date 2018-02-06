from xml.parsers.expat import ParserCreate
from collections import namedtuple
from pyviews.core import CoreError

class XmlNode:
    def __init__(self, namespace, name):
        self.namespace = namespace
        self.name = name
        self.text = ''
        self.children = []
        self.attrs = None

    def get_children(self):
        return self.children

    def get_attrs(self):
        return self.attrs

class XmlAttr:
    def __init__(self, name, value, namespace=None):
        self.namespace = namespace
        self.name = name
        self.value = value

class XmlError(CoreError):
    pass

class Parser:
    Attribute = namedtuple('Attribute', ['name', 'value'])
    Item = namedtuple('Item', ['node', 'namespaces'])
    def __init__(self):
        self._parser = None
        self._root = None
        self._items = []
        self._namespaces = {}

    def _start_element(self, name, attrs):
        attrs = self._get_tuples(attrs)
        self._namespaces = self._get_available_namespaces(attrs)
        (namespace, name) = self._split_namespace(name, True)
        node = XmlNode(namespace, name)
        value_attrs = [a for a in attrs if not a.name.startswith('xmlns')]
        node.attrs = list(self._generate_xml_attributes(value_attrs))
        self._items.append(Parser.Item(node, self._namespaces))

    def _get_tuples(self, attrs):
        key_indexes = list(range(len(attrs)))[0::2]
        return [Parser.Attribute(attrs[i], attrs[i+1]) for i in key_indexes]

    def _get_available_namespaces(self, attrs):
        parent_namespaces = self._items[-1].namespaces if self._items else {}
        nsp_attrs = [a for a in attrs if a.name.startswith('xmlns')]
        namespaces = {a.name: a.value for a in self._remove_xmlns_prefix(nsp_attrs)}
        return {**parent_namespaces, **namespaces}

    def _remove_xmlns_prefix(self, attrs):
        for attr in attrs:
            try:
                key = attr.name.split(':')[1]
            except IndexError:
                key = ''
            yield Parser.Attribute(key, attr.value)

    def _split_namespace(self, name, use_default=False):
        if ':' in name:
            splitted = name.split(':')
            try:
                namespace = self._namespaces[splitted[0]]
            except KeyError:
                format_args = (splitted[0], self._parser.CurrentLineNumber)
                message = 'Unknown xml namespace: {0}. Line {1}'.format(*format_args)
                raise XmlError(message)
            name = splitted[1]
        else:
            try:
                namespace = self._namespaces[''] if use_default else None
            except KeyError:
                format_args = (self._parser.CurrentLineNumber)
                message = 'Unknown default xml namespace. Line {0}'.format(*format_args)
                raise XmlError(message)
        return (namespace, name)

    def _generate_xml_attributes(self, value_attrs):
        for attr in value_attrs:
            (namespace, name) = self._split_namespace(attr.name)
            yield XmlAttr(name, attr.value, namespace)

    def _end_element(self, name):
        node = self._items.pop().node
        try:
            self._items[-1].node.children.append(node)
        except IndexError:
            self._root = node

    def _set_text(self, text):
        node = self._items[-1].node
        node.text = '' if text is None else text.strip()

    def parse(self, xml_file):
        self._parser = ParserCreate()
        self._parser.ordered_attributes = 1
        self._parser.buffer_text = True

        self._parser.StartElementHandler = self._start_element
        self._parser.EndElementHandler = self._end_element
        self._parser.CharacterDataHandler = self._set_text

        self._parser.ParseFile(xml_file)
        root = self._root
        self._reset()
        return root

    def _reset(self):
        self._parser = None
        self._root = None
        self._items = []
        self._namespaces = {}

def get_root(xml_path):
    parser = Parser()
    with open(xml_path, 'rb') as xml_file:
        return parser.parse(xml_file)
