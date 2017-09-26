from unittest import TestCase, main
from xml.etree import ElementTree as ET
from pyviews.core.xml import XmlNode
from pyviews.core.parsing import Node

class TestNode(TestCase):
    def test_init(self):
        element = ET.fromstring('<root xmlns="ns"/>')
        xml_node = XmlNode(element)
        node = Node(xml_node)

        msg = 'Node should inititalise properties from init parameters'
        self.assertEqual(node.xml_node, xml_node, msg)

# class TestDictionary_(TestCase):
#     def test_dictionary_init(self):
#         dictionary = HierarchyDict()

#         self.assertEqual(len(dictionary), 0, 'dictionary length by default should be 0')

#     def test_dictionary_keys(self):
#         dictionary = HierarchyDict()

#         dictionary['one'] = 'one'
#         dictionary['two'] = 2

#         msg = 'Dictionary should get and set values by key'
#         self.assertEqual(dictionary['one'], 'one', msg)
#         self.assertEqual(dictionary['two'], 2, msg)

#         self.assertEqual(len(dictionary), 2, 'dictionary length should be equal to keys count')

#     def test_dictionary_parent(self):
#         parent = HierarchyDict()
#         parent['one'] = 1
#         parent['two'] = 2

#         dictionary = HierarchyDict(parent)
#         dictionary['two'] = 'two'
#         dictionary['three'] = 'three'

#         self.assertEqual(dictionary['one'], 1, 'Dictionary should get values from parent')
#         msg = 'Dictionary should get own value if key exists'
#         self.assertEqual(dictionary['two'], 'two', msg)
#         self.assertEqual(dictionary['three'], 'three', msg)

#         msg = 'dictionary length should be equal to keys count including parent'
#         self.assertEqual(len(dictionary), 3, msg)

#     def test_parent_keys(self):
#         parent = HierarchyDict()
#         parent['one'] = 1
#         parent['two'] = 2

#         dictionary = HierarchyDict(parent)
#         dictionary['two'] = 'two'
#         dictionary['three'] = 'three'

#         msg = 'dictionary should return all keys'
#         self.assertEqual(sorted(dictionary.keys()), sorted(['one', 'two', 'three']), msg)

#     def test_dictionary_items(self):
#         parent = HierarchyDict()
#         parent['one'] = 1
#         parent['two'] = 2

#         dictionary = HierarchyDict(parent)
#         dictionary['two'] = 'two'
#         dictionary['three'] = 'three'

#         actual = sorted(dictionary.items())
#         expected = sorted([('one', 1), ('two', 'two'), ('three', 'three')])
#         self.assertEqual(actual, expected, 'dictionary should return items')

if __name__ == '__main__':
    main()
