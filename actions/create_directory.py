import os

description = {
    "action": "create_directory",
    "description": "Creates a directory with the given name. Can be nested.",
    "arguments": {
        "directory_path": "The name of the file to create.",
    }
}

def create_directory(args):
  path = args.get('directory_path')
  if path:
    try:
      os.makedirs(path)
      return f"Nested directory created: {path}"
    except FileExistsError:
      return f"ERROR: Directory already exists: {path}"
    except Exception as e:
      return f"ERROR: Error creating directory: {e}"
  else:
    return "ERROR: Couldn't create a directory. No path provided."
