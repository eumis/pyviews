"""Binder"""
from abc import abstractmethod, ABC
from typing import Optional, Union

from pyviews.core import BindingError, Node, Modifier, XmlAttr, Binding, InstanceNode


class BindingContext(dict):
    """Used as binding arguments container, passed to binder and rule step"""

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
    def modifier(self) -> Modifier:
        """Modifier"""
        return self.get('modifier', None)

    @modifier.setter
    def modifier(self, value: Modifier):
        self['modifier'] = value

    @property
    def xml_attr(self) -> XmlAttr:
        """Xml attribute"""
        return self.get('xml_attr', None)

    @xml_attr.setter
    def xml_attr(self, value: XmlAttr):
        self['xml_attr'] = value


class BindingRule(ABC):
    """Creates binding for args"""

    @abstractmethod
    def suitable(self, context: BindingContext) -> bool:
        """Returns True if rule is suitable for args"""

    @abstractmethod
    def apply(self, context: BindingContext) -> Binding:
        """Applies binding"""


class Binder:
    """Applies binding"""

    def __init__(self):
        self._rules = {}

    def add_rule(self, binding_type: str, rule: BindingRule):
        """Adds new rule"""
        if binding_type not in self._rules:
            self._rules[binding_type] = []

        self._rules[binding_type].insert(0, rule)

    def find_rule(self, binding_type: str, context: BindingContext) -> Optional[BindingRule]:
        """Finds rule by binding type and args"""
        try:
            rules = self._rules[binding_type]
            return next(rule for rule in rules if rule.suitable(context))
        except (KeyError, StopIteration):
            return None

    def apply(self, binding_type, context: BindingContext):
        """Returns apply function"""
        rule = self.find_rule(binding_type, context)
        if rule is None:
            raise self._get_not_found_error(context, binding_type)
        binding = rule.apply(context)
        if binding:
            context.node.add_binding(binding)

    @staticmethod
    def _get_not_found_error(args, binding_type):
        error = BindingError('Binding rule is not found')
        error.add_info('Binding type', binding_type)
        error.add_info('args', args)
        return error
