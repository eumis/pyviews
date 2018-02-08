from xml.parsers.expat import ParserCreate, ExpatError, errors
from collections import namedtuple
from pyviews.core import CoreError

class XmlNode:
    def __init__(self, namespace, name):
        self.namespace = namespace
        self.name = name
        self.text = ''
        self.children = []
        self.attrs = []

class XmlAttr:
    def __init__(self, name, value=None, namespace=None):
        self.namespace = namespace
        self.name = name
        self.value = value

class XmlError(CoreError):
    UnknownNamespace = 'Unknown xml namespace: {0}.'
    UnknownDefaultNamespace = 'Unknown default xml namespace.'
    def __init__(self, message, linenumber):
        super().__init__(message, 'Line {0}.'.format(linenumber))

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
                message = XmlError.UnknownNamespace.format(splitted[0])
                raise XmlError(message, self._parser.CurrentLineNumber)
            name = splitted[1]
        else:
            try:
                namespace = self._namespaces[''] if use_default else None
            except KeyError:
                raise XmlError(XmlError.UnknownDefaultNamespace, self._parser.CurrentLineNumber)
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
        self._setup_parser()
        try:
            self._parser.ParseFile(xml_file)
        except ExpatError as error:
            raise XmlError(errors.messages[error.code], error.lineno)

        root = self._root
        self._reset()
        return root

    def _setup_parser(self):
        self._parser = ParserCreate()
        self._parser.ordered_attributes = 1
        self._parser.buffer_text = True

        self._parser.StartElementHandler = self._start_element
        self._parser.EndElementHandler = self._end_element
        self._parser.CharacterDataHandler = self._set_text

    def _reset(self):
        self._parser = None
        self._root = None
        self._items = []
        self._namespaces = {}

def get_root(xml_path):
    parser = Parser()
    with open(xml_path, 'rb') as xml_file:
        return parser.parse(xml_file)
