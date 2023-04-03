# actions/create_file.py
import os

description = {
  "action": "create_file",
  "description": "Creates a file with the given name.",
  "arguments": {
    "file_path": "The path/name of the file to create. This should be a relative path from the working directory.",
  }
}

working_directory = "/Users/username/Projects/my_project"

def create_file(args):
  file_path = args.get('file_path')
  if file_path:
    with open(file_path, 'w') as f:
      f.write('')
    return f"Created a file at '{file_path}'."
  else:
    return "ERROR: Couldn't create a file. No path provided."
