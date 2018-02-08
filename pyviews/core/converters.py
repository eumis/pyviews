'''Value converters used for binding'''

def to_int(value):
    '''Converts string value to int'''
    if value and value.strip():
        return int(value)
    return None
