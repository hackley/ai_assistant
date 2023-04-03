description = {
    "action": "write_to_file",
    "description": "Replaces the contents of a file with the given content. Returns 'true' if successful or an error message if the action fails.",
    "arguments": {
        "file_path": "Relative path to the file you want to write to.",
        "content": "The content you want to write to the file. Use double backslashes (\\\\) to escape newline characters (\\\\n) within the content."
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
