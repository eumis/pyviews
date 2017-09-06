class Expression:
    def __init__(self, code, parameters=None):
        self.code = code
        self._parameters = {} if parameters is None else parameters

    def get_parameters(self):
        return self._parameters.copy()

    def compile(self, parameters=None):
        params = self.get_parameters()
        params.update(parameters)
        eval(self.code, params, {})
