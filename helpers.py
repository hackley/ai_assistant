import os
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


def check_directory_permission(file_path, settings):
    """Checks if the given file_path is within the specified working directory.

    :param file_path: The path to the file being checked.
    :param working_dir: The working directory.
    :return: True if the file_path is within the working directory, False otherwise.
    :return: The normalized file path.
    """
    working_dir = settings["working_directory"]
    full_file_path = os.path.join(working_dir, file_path)
    normalized_file_path = os.path.normpath(os.path.abspath(full_file_path))
    return normalized_file_path.startswith(working_dir), normalized_file_path
