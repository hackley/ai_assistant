import importlib

def to_camel_case(string):
    words = string.split('_')
    return ''.join(word.capitalize() for word in words)

def init_tool(tool_file, settings):
    module_name = tool_file.stem
    if module_name in settings['enabled_tools']:
        klass_name = to_camel_case(module_name)
        tool_module = importlib.import_module(module_name)
        klass = getattr(tool_module, klass_name)
        return klass(settings)
    else:
        return None