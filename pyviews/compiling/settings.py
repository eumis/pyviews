class CompileSettings:
    def __init__(self):
        self._actions = []

_SETTINGS = CompileSettings()

def edit(edit_method):
    edit_method(_SETTINGS)

def get_settings():
    return _SETTINGS
