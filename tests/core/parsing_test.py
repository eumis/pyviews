from unittest import TestCase, main
from xml.etree import ElementTree as ET
from pyviews.core.xml import XmlNode
from pyviews.core.parsing import Globals, Node

class TestGlobals(TestCase):
    def test_globals_keys(self):
        parent = Globals()
        parent['one'] = 1
        parent['two'] = 2

        globs = Globals(parent)
        globs['two'] = 'two'
        globs['three'] = 'three'

        self.assertEqual(globs['one'], 1, 'Globals should get values from parent')
        msg = 'Globals should get own value if key exists'
        self.assertEqual(globs['two'], 'two', msg)
        self.assertEqual(globs['three'], 'three', msg)

    def test_parent_keys(self):
        parent = Globals()
        parent['one'] = 1
        parent['two'] = 2

        globs = Globals(parent)
        globs['two'] = 'two'
        globs['three'] = 'three'

        msg = 'own_keys should return only own keys'
        self.assertEqual(sorted(globs.own_keys()), sorted(['two', 'three']), msg)

        msg = 'all_keys should return own keys plus parent keys'
        self.assertEqual(sorted(globs.all_keys()), sorted(['one', 'two', 'three']), msg)

    def test_dictionary(self):
        parent = Globals()
        parent['one'] = 1
        parent['two'] = 2

        globs = Globals(parent)
        globs['two'] = 'two'
        globs['three'] = 'three'

        msg = 'to_dictionary should return dictionary with own keys'
        self.assertEqual(globs.to_dictionary(), {'two': 'two', 'three': 'three'}, msg)

        msg = 'to_all_dictionary should return dictionary with all keys'
        self.assertEqual(globs.to_all_dictionary(), {'one': 1, 'two': 'two', 'three': 'three'}, msg)

class TestNode(TestCase):
    def test_init(self):
        element = ET.fromstring('<root xmlns="ns"/>')
        xml_node = XmlNode(element)
        node = Node(xml_node)

        msg = 'Node should inititalise properties from init parameters'
        self.assertEqual(node.xml_node, xml_node, msg)

if __name__ == '__main__':
    main()
