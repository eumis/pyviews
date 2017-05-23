from common.reflection.activator import create

def compile_view(root):
    res = root.tag.split('}')
    return create(res[0][1:], res[1])
