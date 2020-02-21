"""Xml parsing"""

# pylint:disable=wrong-import-order
from collections import namedtuple
from typing import List, Tuple, NamedTuple, Generator
from xml.parsers.expat import ParserCreate, ExpatError

from .error import PyViewsError, ViewInfo


class XmlAttr(NamedTuple):
    """Parsed xml attribute"""
    name: str
    value: str = None
    namespace: str = None


class XmlNode(NamedTuple):
    """Parsed xml node"""
    namespace: str
    name: str
    text: str = ''
    children: List['XmlNode'] = []
    attrs: List[XmlAttr] = []
    view_info: ViewInfo = None


class XmlError(PyViewsError):
    """Describes xml parsing error"""


ElementAttr = namedtuple('ElementAttr', ['name', 'value'])
Element = namedtuple('Element', ['node', 'namespaces'])


class Parser:
    """Wrapper under xml.parsers.expat for parsing xml files"""

    def __init__(self):
        self._parser = None
        self._root = None
        self._elements: List[Element] = []
        self._namespaces = {}
        self._view_name = None

    def parse(self, xml_file, view_name: str = None) -> XmlNode:
        """Parses xml file with xml_path and returns XmlNode"""
        self._setup_parser()
        try:
            self._view_name = view_name
            self._parser.ParseFile(xml_file)
        except ExpatError as error:
            raise XmlError(str(error), ViewInfo(view_name, error.lineno))

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

    def _start_element(self, full_name: str, keys: List[str]):
        attrs = self._convert_to_attributes(keys)
        self._namespaces = self._get_available_namespaces(attrs)
        node = self._create_xml_node(full_name, attrs)
        self._elements.append(Element(node, self._namespaces))

    @staticmethod
    def _convert_to_attributes(keys: List[str]) -> List[ElementAttr]:
        key_indexes = list(range(len(keys)))[0::2]
        return [ElementAttr(keys[i], keys[i + 1]) for i in key_indexes]

    def _create_xml_node(self, full_name: str, attrs: List[ElementAttr]) -> XmlNode:
        (namespace, name) = self._get_namespace_and_name(full_name, True)
        value_attrs = list(self._get_attributes(attrs))
        view_info = ViewInfo(self._view_name, self._parser.CurrentLineNumber)
        return XmlNode(namespace, name, '', [], value_attrs, view_info)

    def _get_namespace_and_name(self, full_name: str, use_default=False) -> Tuple[str, str]:
        if ':' in full_name:
            return self._split(full_name)
        namespace = self._get_default_namespace() if use_default else None
        return namespace, full_name

    def _split(self, full_name: str) -> Tuple[str, str]:
        parts = full_name.split(':')
        try:
            return self._namespaces[parts[0]], parts[1]
        except KeyError:
            raise XmlError(f'Unknown xml namespace: {parts[0]}', self._get_view_info())

    def _get_default_namespace(self) -> str:
        try:
            return self._namespaces['']
        except KeyError:
            raise XmlError('Unknown default xml namespace', self._get_view_info())

    def _get_attributes(self, attributes: List[ElementAttr]) -> Generator[XmlAttr, None, None]:
        value_attrs = [a for a in attributes if not a.name.startswith('xmlns')]
        for attr in value_attrs:
            (namespace, name) = self._get_namespace_and_name(attr.name)
            yield XmlAttr(name, attr.value, namespace)

    def _get_available_namespaces(self, attrs: List[ElementAttr]):
        parent_namespaces = self._elements[-1].namespaces if self._elements else {}
        nsp_attrs = [a for a in attrs if a.name.startswith('xmlns')]
        namespaces = {a.name: a.value for a in self._remove_xmlns_prefix(nsp_attrs)}
        return {**parent_namespaces, **namespaces}

    @staticmethod
    def _remove_xmlns_prefix(attrs) -> Generator[ElementAttr, None, None]:
        for attr in attrs:
            try:
                key = attr.name.split(':')[1]
            except IndexError:
                key = ''
            yield ElementAttr(key, attr.value)

    def _end_element(self, _):
        node = self._elements.pop().node
        try:
            self._elements[-1].node.children.append(node)
        except IndexError:
            self._root = node

    def _set_text(self, text):
        if text:
            item = self._elements[-1]
            # noinspection PyProtectedMember
            node = item.node._replace(text=text)
            self._elements[-1] = Element(node, item.namespaces)

    def _reset(self):
        self._parser = None
        self._root = None
        self._elements = []
        self._namespaces = {}

    def _get_view_info(self):
        return ViewInfo(self._view_name, self._parser.CurrentLineNumber)
