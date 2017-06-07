from os.path import abspath, join
from pyviews.compiling.view import compile_view as compile_xml_view, render_view as render_xml_view
from pyviews.compiling.parser import parse_xml
from pyviews.common.values import VIEW_EXT

def init(views_folder, app_view='app'):
    global VIEWS_PATH
    VIEWS_PATH = abspath(views_folder)
    global app
    app = compile_view(app_view)

def compile_view(view, parent=None):
    view_path = get_view_path(view)
    xml_node = parse_xml(view_path)
    return compile_xml_view(xml_node, parent)

def get_view_path(view):
    return join(VIEWS_PATH, view + VIEW_EXT)

def show_view(view):
    render_view(view, app)

def render_view(view, parent_node):
    view_path = get_view_path(view)
    xml_node = parse_xml(view_path)
    return render_xml_view(xml_node, parent_node)

def load_styles(path):
    node = compile_view(path)
    return node.context.styles

def run():
    app.run()
