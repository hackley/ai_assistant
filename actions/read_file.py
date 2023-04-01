description = {
    "action": "read_file",
    "description": "This action reads a file and returns its contents. You will receive a message from 'system' with the contents of the file.",
    "arguments": {
        "file_path": "Relative path to the file you want to read.",
    }
}

def read_file(args):
  path = args.get('file_path')
  if path:
    with open(path, 'r') as file:
      content = file.read()
      return content
  else:
    return "ERROR: Couldn't create a directory. No path provided."
