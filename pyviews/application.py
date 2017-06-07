from os.path import abspath, join
from pyviews.compiling.view import compile_view as compile_xml_view
from pyviews.compiling.parser import parse_xml
from pyviews.common.values import VIEW_EXT

def init(views_folder, app_view='app'):
    global VIEWS_PATH
    VIEWS_PATH = abspath(views_folder)
    app_view_path = get_view_path(app_view)
    global app
    app = compile_view(app_view_path)

def get_view_path(view):
    return join(VIEWS_PATH, view + VIEW_EXT)

def show_view(view):
    view_path = get_view_path(view)
    compile_view(view_path, app)

def compile_view(xml_path, parent=None):
    xml_node = parse_xml(xml_path)
    return compile_xml_view(xml_node, parent)

def load_styles(path):
    xml_path = get_view_path(path)
    node = compile_view(xml_path)
    return node.context.styles

def run():
    app.run()
