from tempfile import TemporaryFile
from unittest import TestCase, main
from tests.utility import case
from pyviews.core.customxml import Parser

class ParsingTests(TestCase):
    @case('<someroot xmlns="somenamespace"><somenode /></someroot>')
    def test_hoho(self, xml_string):
        parser = Parser()

        with TemporaryFile() as xml_file:
            xml_file.write(xml_string.encode())
            xml_file.seek(0)
            root = parser.parse(xml_file)
            print(root)

if __name__ == '__main__':
    main()
