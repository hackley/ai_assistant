# actions/create_file.py
import os

description = {
  "action": "create_file",
  "description": "Creates a file with the given name.",
  "arguments": {
    "file_name": "The name of the file to create.",
  }
}

def create_file(args):
  file_name = args.get('file_name')
  if file_name:
    with open(file_name, 'w') as f:
      f.write('')
    return f"Created a file named '{file_name}'."
  else:
    return "Couldn't create a file. No name provided."
