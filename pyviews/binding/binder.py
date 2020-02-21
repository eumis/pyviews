"""Binder"""

from typing import Optional, Union, Callable, NamedTuple

from pyviews.core import BindingError, Node, Setter, XmlAttr, Binding, InstanceNode


class BindingContext(dict):
    """Used as binding arguments passed to binder and rule step"""

    @property
    def node(self) -> Union[Node, InstanceNode]:
        """Node"""
        return self.get('node', None)

    @node.setter
    def node(self, value: Union[Node, InstanceNode]):
        self['node'] = value

    @property
    def expression_body(self) -> str:
        """Expression body from attribute value"""
        return self.get('expression_body', None)

    @expression_body.setter
    def expression_body(self, value: str):
        self['expression_body'] = value

    @property
    def setter(self) -> Setter:
        """Setter"""
        return self.get('setter', None)

    @setter.setter
    def setter(self, value: Setter):
        self['setter'] = value

    @property
    def xml_attr(self) -> XmlAttr:
        """Xml attribute"""
        return self.get('xml_attr', None)

    @xml_attr.setter
    def xml_attr(self, value: XmlAttr):
        self['xml_attr'] = value


class BindingRule(NamedTuple):
    """Creates binding for args"""
    suitable: Callable[[BindingContext], bool]
    bind: Callable[[BindingContext], Union[Binding]]


class Binder:
    """Applies binding"""

    def __init__(self):
        self._rules = {}

    def add_rule(self, binding_type: str, bind: Callable[[BindingContext], Union[Binding, None]],
                 suitable: Callable[[BindingContext], bool] = None):
        """Adds new rule"""
        suitable = suitable if suitable else lambda _: True
        if binding_type not in self._rules:
            self._rules[binding_type] = []

        self._rules[binding_type].insert(0, BindingRule(suitable, bind))

    def bind(self, binding_type: str, context: BindingContext):
        """Returns apply function"""
        rule = self._find_rule(binding_type, context)
        binding = rule.bind(context)
        if binding:
            context.node.add_binding(binding)

    def _find_rule(self, binding_type: str, context: BindingContext) -> Optional[BindingRule]:
        """Finds rule by binding type and args"""
        try:
            rules = self._rules[binding_type]
            return next(rule for rule in rules if rule.suitable(context))
        except (KeyError, StopIteration):
            error = BindingError('Binding rule is not found')
            error.add_info('Binding type', binding_type)
            error.add_info('Binding context', context)
            raise error
