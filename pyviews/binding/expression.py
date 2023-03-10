"""Expression binding"""

import ast
from functools import partial
from re import compile as compile_regex
from typing import Any, Callable, Dict, List, NamedTuple, Set, Union

from pyviews.binding.binder import BindingContext
from pyviews.core.bindable import Bindable, BindableRecord, recording
from pyviews.core.binding import Binding, BindingCallback, BindingError
from pyviews.core.error import PyViewsError, error_handling
from pyviews.core.expression import Expression, execute
from pyviews.core.rendering import NodeGlobals

ROOT = 'root'
ENTRY = 'entry'
ATTRIBUTE = 'attribute'
INDEX = 'index'

_GET_VALUE = {
    ENTRY: lambda inst, key: inst.get(key),
    ATTRIBUTE: getattr,
    INDEX: lambda inst, key: inst[key]
} # yapf: disable

_AST_CLASSES = {ast.Name, ast.Attribute, ast.Subscript}


class ObjectNode(NamedTuple):
    """Root entry in expression"""
    key: str
    type: str
    children: List['ObjectNode']


_OBJECT_NODE_CACHE: Dict[str, ObjectNode] = {}


def _level_key(ast_node: ast.AST):
    level = 0
    while hasattr(ast_node, 'value'):
        level = level + 1
        ast_node = ast_node.value
    return level


def _get_index_value(ast_node: ast.Subscript) -> Any:
    ast_node = ast_node.slice.value if isinstance(ast_node.slice, ast.Index) else ast_node.slice
    if isinstance(ast_node, ast.Constant):
        return ast_node.value
    if isinstance(ast_node, ast.Num):
        return ast_node.n
    return _get_attr_expression(ast_node)


def _get_attr_expression(ast_node: Union[ast.Name, ast.Attribute, ast.Subscript]) -> 'Expression':
    result = ''
    while isinstance(ast_node, ast.Attribute):
        result = f'.{ast_node.attr}{result}'
        ast_node = ast_node.value
    return Expression(f'{ast_node.id}{result}')


def _get_object_tree(code: str) -> ObjectNode:
    if code in _OBJECT_NODE_CACHE:
        return _OBJECT_NODE_CACHE[code]
    root = ObjectNode('root', ROOT, [])
    ast_root = ast.parse(code)
    nodes: Dict[ast.AST, ObjectNode] = {}
    ast_nodes = sorted((item for item in ast.walk(ast_root) if item.__class__ in _AST_CLASSES), key = _level_key)
    for ast_node in ast_nodes:
        if isinstance(ast_node, ast.Name):
            try:
                node = next(n for n in root.children if n.key == ast_node.id)
            except StopIteration:
                node = ObjectNode(ast_node.id, ENTRY, [])
                root.children.append(node)
            nodes[ast_node] = node
        if isinstance(ast_node, ast.Attribute):
            ast_parent = ast_node.value
            try:
                node = next(n for n in nodes[ast_parent].children if n.key == ast_node.attr)
            except StopIteration:
                node = ObjectNode(ast_node.attr, ATTRIBUTE, [])
                nodes[ast_parent].children.append(node)
            nodes[ast_node] = node
        if isinstance(ast_node, ast.Subscript):
            ast_parent = ast_node.value
            key = _get_index_value(ast_node)
            try:
                node = next(n for n in nodes[ast_parent].children if n.key == key)
            except StopIteration:
                node = ObjectNode(key, INDEX, [])
                nodes[ast_parent].children.append(node)
            nodes[ast_node] = node
    _OBJECT_NODE_CACHE[code] = root
    return root


class ExpressionBinding(Binding):
    """Binds target to expression result"""

    def __init__(self, callback: BindingCallback, expression: Expression, expr_vars: NodeGlobals):
        super().__init__()
        self._callback: BindingCallback = callback
        self._expression: Expression = expression
        self._destroy_functions: List[Callable] = []
        self._vars: NodeGlobals = expr_vars

    def bind(self, execute_callback = True):
        self.destroy()
        with recording() as records:
            value = execute(self._expression, self._vars)
        with error_handling(BindingError, self._add_error_info):
            self._create_dependencies(records)
        if execute_callback:
            self._callback(value)

    def _create_dependencies(self, records: Set[BindableRecord]):
        for record in records:
            self._subscribe_for_changes(record.bindable, record.key)

    def _subscribe_for_changes(self, inst: Bindable, key: str):
        try:
            inst.observe(key, self._update_callback)
            self._destroy_functions.append(partial(inst.release, key, self._update_callback))
        except KeyError:
            pass

    def _update_callback(self, new_val, old_val):
        with error_handling(BindingError, self._add_error_info):
            if isinstance(new_val, Bindable) or isinstance(old_val, Bindable):
                self.bind()
            else:
                self._execute_callback()

    def _add_error_info(self, error: PyViewsError):
        error.add_info('Binding', self)
        error.add_info('Expression', self._expression.code)
        error.add_info('Callback', self._callback)

    def _execute_callback(self):
        value = execute(self._expression, self._vars)
        self._callback(value)

    def destroy(self):
        for destroy in self._destroy_functions:
            destroy()
        self._destroy_functions = []


def bind_setter_to_expression(context: BindingContext) -> Binding:
    """Binds callback to expression result changes"""
    expr = Expression(context.expression_body)
    callback = partial(context.setter, context.node, context.xml_attr.name)
    binding = ExpressionBinding(callback, expr, context.node.node_globals)
    binding.bind()
    return binding


PROPERTY_EXPRESSION_REGEX = compile_regex(r'([a-zA-Z_0-9]{1,}\.){0,}([a-zA-Z_0-9]{1,})')


def get_expression_callback(expression: Expression, expr_vars: NodeGlobals) -> BindingCallback:
    """Returns callback that sets value to property expression"""
    _validate_property_expression(expression.code)
    object_tree = _get_object_tree(expression.code)
    if object_tree.children[0].children:
        return partial(_property_expression_callback, object_tree, expr_vars)
    return partial(_on_global_value_update, expr_vars, expression.code)


def _validate_property_expression(source_code: str):
    if not PROPERTY_EXPRESSION_REGEX.fullmatch(source_code):
        error = BindingError('Expression should be property expression')
        error.add_info('Expression', source_code)
        raise error


def _property_expression_callback(_var_tree: ObjectNode, _vars: NodeGlobals, value: Any):
    (inst, prop) = _get_target(_var_tree, _vars)
    setattr(inst, prop, value)


def _get_target(var_tree: ObjectNode, expr_vars: NodeGlobals):
    entry = var_tree.children[0]
    inst = expr_vars[entry.key]
    next_key = entry.children[0].key
    entry = entry.children[0]

    while entry.children:
        inst = getattr(inst, next_key)
        next_key = entry.children[0].key
        entry = entry.children[0]

    return inst, next_key


def _on_global_value_update(_vars: NodeGlobals, key: str, value):
    _vars[key] = value
