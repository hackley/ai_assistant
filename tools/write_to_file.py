import os
from tool import Tool


class WriteToFile(Tool):
    name = "WriteToFile"
    description = '''
      Replaces the contents of a file and returns 'true' if successful.
      `args` should be a dictionary with the following keys: file_path, content.
    '''

    def _run(self, args: dict) -> str:
        """Use the tool."""
        file_path = args.get("file_path")
        content = args.get("content")
        if file_path and content is not None:
            try:
                with open(file_path, 'w') as file:
                  file.write(content)
                return "true"
            except Exception as e:
                return f"ERROR: {e}"
        else:
            return f"ERROR: missing arguments"
