import os

description = {
    "action": "delete_file",
    "description": "Deletes a file.",
    "arguments": {
        "file_name": "The relative path of the file to delete.",
    }
}


def delete_file(args):
  file_name = args.get('file_name')

  # Safety first!
  if file_name.startswith('tmp/') == False:
    return "ERROR: Couldn't delete file. Only the tmp directory can be accessed."

  if file_name:
    if os.path.isfile(file_name):
      os.remove(file_name)
      return f"Deleted a file named '{file_name}'."
    else:
      return f"ERROR: Couldn't delete file. File '{file_name}' does not exist."
  else:
    return "ERROR: Couldn't delete file. No path provided."
