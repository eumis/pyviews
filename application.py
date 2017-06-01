from os.path import abspath, join
from parsing.compiler import compile_view as compile_xml_view
from parsing.parser import parse_xml
from common.values import VIEW_EXT

def init(views_folder, app_view='app'):
    global VIEWS_PATH
    VIEWS_PATH = abspath(views_folder)
    app_view_path = get_view_path(app_view)
    global app
    app = compile_view(app_view_path)

def get_view_path(view):
    return join(VIEWS_PATH, view + VIEW_EXT)

def show_view(view):
    app.clear()
    view_path = get_view_path(view)
    compile_view(view_path, app)

def compile_view(xml_path, parent=None):
    xml_node = parse_xml(xml_path)
    return compile_xml_view(xml_node, parent)

def run():
    app.run()
