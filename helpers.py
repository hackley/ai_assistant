def to_camel_case(string):
    words = string.split('_')
    return ''.join(word.capitalize() for word in words)
