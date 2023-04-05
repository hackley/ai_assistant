from tool import Tool
from helpers import check_directory_permission


class WriteToFile(Tool):
    name = "WriteToFile"
    description = '''
      Replaces the contents of a file and returns 'true' if successful.
      Useful for helping the user write code. 
      Remember to always send the full file contents when using this tool.
      `args` should be a dictionary with the following keys: file_path, content.
    '''

    def _run(self, args: dict) -> str:
        """Use the tool."""
        file_path = args.get("file_path")
        content = args.get("content")
        if file_path and content is not None:
            dir_allowed, normalized_file_path = check_directory_permission(
                file_path, self.settings)
            if not dir_allowed:
                return "ERROR: Writing to a file outside of the working_directory is not allowed."
            try:
                with open(normalized_file_path, 'w') as file:
                  file.write(content)
                return "true"
            except Exception as e:
                return f"ERROR: {e}"
        else:
            return f"ERROR: missing arguments"
