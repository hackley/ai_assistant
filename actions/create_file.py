# actions/create_file.py
import os

description = {
  "action": "create_file",
  "description": "Creates a file with the given name.",
  "arguments": {
    "file_path": "The path/name of the file to create. This should be a relative path from the working directory.",
  }
}

working_directory = "/Users/nathan/Code/assistant/tmp/project"

def create_file(args):
  file_path = args.get('file_path')
  if file_path:
    full_file_path = os.path.join(working_directory, file_path)
    normalized_file_path = os.path.normpath(os.path.abspath(full_file_path))

    if normalized_file_path.startswith(working_directory):
      with open(normalized_file_path, 'w') as f:
        f.write('')
      return f"Created a file at '{normalized_file_path}'."
    else:
      return "ERROR: Attempt to create a file outside the working_directory is not allowed."
  else:
    return "ERROR: Couldn't create a file. No path provided."