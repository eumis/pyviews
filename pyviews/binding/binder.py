from pyviews.core import BindingRule, BindingError


class Binder:
    """Applies binding"""

    def __init__(self):
        self._rules = {}

    def add_rule(self, binding_type: str, rule: BindingRule):
        """Adds new rule"""
        if binding_type not in self._rules:
            self._rules[binding_type] = []

        self._rules[binding_type].insert(0, rule)

    def find_rule(self, binding_type: str, **args):
        """Finds rule by binding type and args"""
        try:
            rules = self._rules[binding_type]
            return next(rule for rule in rules if rule.suitable(**args))
        except (KeyError, StopIteration):
            return None

    def apply(self, binding_type, **args):
        """Returns apply function"""
        rule = self.find_rule(binding_type, **args)
        if rule is None:
            raise self._get_not_found_error(args, binding_type)
        binding = rule.apply(**args)
        if binding:
            args['node'].add_binding(rule.apply(**args))

    @staticmethod
    def _get_not_found_error(args, binding_type):
        error = BindingError('Binding rule is not found')
        error.add_info('Binding type', binding_type)
        error.add_info('args', args)
        return error
