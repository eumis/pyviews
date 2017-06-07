from pyviews.compiling.widget import compile_widget

def compile_view(node, parent=None, view_model=None):
    view_model = parent.view_model if parent and not view_model else view_model
    return compile_widget(node, parent, view_model)

def render_view(node, parent, view_model=None):
    view_model = parent.view_model if parent and not view_model else view_model
    parent.render(lambda parent: [compile_widget(node, parent, view_model)])
