def parse_tag(expression):
    type_desc = expression.split('}')
    return (type_desc[0][1:], type_desc[1])

def parse_attr(expression):
    return expression.split(":")
