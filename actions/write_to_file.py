description = {
    "action": "write_to_file",
    "description": "This action replaces the contents of a file and returns 'true' if successful. An error message will be returned if the action fails.",
    "arguments": {
        "file_path": "Relative path to the file you want to write to.",
        "content": "The content you want to write to the file."
    }
}


def write_to_file(args):
  file_path = args.get('file_path')
  content = args.get('content')

  if file_path and content is not None:
    try:
      with open(file_path, 'w') as file:
        file.write(content)
      return "true"
    except Exception as e:
      return f"ERROR: {e}"
  else:
    return f"ERROR: missing arguments"
