from pyviews.view.base import CompileNode

def find_node(node_id):
    return CompileNode.nodes[node_id] if node_id in CompileNode.nodes else None

def scroll_to(scroll_node, node):
    node = node if isinstance(node, CompileNode) else find_node(node)
    widget = node.get_widget() if node else None
    if widget and scroll_node:
        scroll_node.scroll_to(widget)

def scroll_to_fraction(scroll_node, fraction):
    if scroll_node:
        scroll_node.scroll_to_fraction(fraction)
