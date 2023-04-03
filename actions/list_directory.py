import os

description = {
  "action": "list_directory",
  "description": "Lists the contents of a directory.",
  "arguments": {
    "directory_path": "The path of the directory to list.",
  }
}

def list_directory(args):
  directory_path = args.get('directory_path')
  if directory_path:
    try:
      contents = os.listdir(directory_path)
      return contents
    except Exception as e:
      return f"ERROR: Couldn't list directory contents: {e}"
  else:
    return "ERROR: No directory path provided."