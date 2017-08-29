def case(*params):
    def case_decorator(func):
        def decorated(*args):
            for params in decorated.params:
                case_params = args + params
                try:
                    func(*case_params)
                except AssertionError as error:
                    error.args = error.args + params
                    raise error
        if func.__name__ == 'decorated':
            func.params.append(params)
            return func
        decorated.params = [params]
        return decorated
    return case_decorator
