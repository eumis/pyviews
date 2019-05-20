"""Xml parsing"""
from typing import List, Tuple
from xml.parsers.expat import ParserCreate, ExpatError, errors
from collections import namedtuple
from injectool import inject
from .error import CoreError, ViewInfo


class XmlNode:
    """Parsed xml node"""

    def __init__(self, namespace, name):
        self.namespace = namespace
        self.name = name
        self.text = ''
        self.children = []
        self.attrs = []
        self.view_info = None


class XmlAttr:
    """Parsed xml attribute"""

    def __init__(self, name, value=None, namespace=None):
        self.namespace = namespace
        self.name = name
        self.value = value


class XmlError(CoreError):
    """Describes xml parsing error"""
    Unknown_namespace = 'Unknown xml namespace: {0}.'
    Unknown_default_namespace = 'Unknown default xml namespace.'


Attribute = namedtuple('Attribute', ['name', 'value'])
Item = namedtuple('Item', ['node', 'namespaces'])


class Parser:
    """Wrapper under xml.parsers.expat for parsing xml files"""

    @inject('namespaces')
    def __init__(self, namespaces: dict = None):
        self._parser = None
        self._root = None
        self._items = []
        self._predefined_namespaces = namespaces if namespaces else {}
        self._namespaces = {}
        self._view_name = None

    def _start_element(self, full_name, attrs):
        attrs = self._get_tuples(attrs)
        self._namespaces = self._get_available_namespaces(attrs)
        (namespace, name) = self._split_namespace(full_name, True)
        node = XmlNode(namespace, name)
        node.view_info = ViewInfo(self._view_name, self._parser.CurrentLineNumber)
        value_attrs = [a for a in attrs if not a.name.startswith('xmlns')]
        node.attrs = list(self._generate_xml_attributes(value_attrs))
        self._items.append(Item(node, self._namespaces))

    @staticmethod
    def _get_tuples(attrs) -> List[Attribute]:
        key_indexes = list(range(len(attrs)))[0::2]
        return [Attribute(attrs[i], attrs[i + 1]) for i in key_indexes]

    def _get_available_namespaces(self, attrs):
        parent_namespaces = self._items[-1].namespaces if self._items else {}
        nsp_attrs = [a for a in attrs if a.name.startswith('xmlns')]
        namespaces = {a.name: a.value for a in self._remove_xmlns_prefix(nsp_attrs)}
        return {**self._predefined_namespaces, **parent_namespaces, **namespaces}

    @staticmethod
    def _remove_xmlns_prefix(attrs) -> List[Attribute]:
        for attr in attrs:
            try:
                key = attr.name.split(':')[1]
            except IndexError:
                key = ''
            yield Attribute(key, attr.value)

    def _split_namespace(self, name, use_default=False) -> Tuple[str, str]:
        if ':' in name:
            parts = name.split(':')
            try:
                namespace = self._namespaces[parts[0]]
            except KeyError:
                message = XmlError.Unknown_namespace.format(parts[0])
                raise XmlError(message, self._get_view_info())
            name = parts[1]
        else:
            try:
                namespace = self._namespaces[''] if use_default else None
            except KeyError:
                raise XmlError(XmlError.Unknown_default_namespace, self._get_view_info())
        return namespace, name

    def _generate_xml_attributes(self, value_attrs):
        for attr in value_attrs:
            (namespace, name) = self._split_namespace(attr.name)
            yield XmlAttr(name, attr.value, namespace)

    def _end_element(self, _):
        node = self._items.pop().node
        try:
            self._items[-1].node.children.append(node)
        except IndexError:
            self._root = node

    def _set_text(self, text):
        node = self._items[-1].node
        node.text = '' if text is None else text

    def parse(self, xml_file, view_name=None) -> XmlNode:
        """Parses xml file with xml_path and returns XmlNode"""
        self._setup_parser()
        try:
            self._view_name = view_name
            self._parser.ParseFile(xml_file)
        except ExpatError as error:
            raise XmlError(errors.messages[error.code], ViewInfo(view_name, error.lineno))

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

    def _get_view_info(self):
        return ViewInfo(self._view_name, self._parser.CurrentLineNumber)
