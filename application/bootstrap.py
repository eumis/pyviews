from os.path import abspath, join
from parsing.compiler import compile_view
from parsing.parser import parse_xml
from common.values import VIEW_EXT



class App:
    def __init__(self, views_folder, app_view='app'):
        self._views_folder = abspath(views_folder)
        app_view_path = self.get_view_path(app_view)
        self._tk = load_view(app_view_path)

    def get_view_path(self, view):
        return join(self._views_folder, view + VIEW_EXT)

    def show_view(self, view):
        self._tk.clear()
        view_path = self.get_view_path(view)
        load_view(view_path, self._tk)

    def run(self):
        self._tk.run()

def load_view(xml_path, parent=None):
    xml_node = parse_xml(xml_path)
    return compile_view(xml_node, parent)
