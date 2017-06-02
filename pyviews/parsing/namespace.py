def has_namespace(name):
    return name.startswith('{')

def parse_namespace(name):
    splitted = name.split('}', maxsplit=1)
    name_space = splitted[0][1:]
    name = splitted[1]
    return (name_space, name)
