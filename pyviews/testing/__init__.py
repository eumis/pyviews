'''Utility for unit testing pyviews'''

def case(*params):
    '''Passes parameters to test method. In case several decorators wraps every case to sub test'''
    def _case_decorator(func):
        def _decorated(*args):
            for params in reversed(_decorated.params):
                case_params = args + params
                try:
                    with args[0].subTest(case=params):
                        func(*case_params)
                except AssertionError as error:
                    error.args = error.args + params
                    raise error
        if func.__name__ == '_decorated':
            func.params.append(params)
            return func
        _decorated.params = [params]
        return _decorated
    return _case_decorator
