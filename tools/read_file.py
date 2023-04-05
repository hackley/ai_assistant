from tool import Tool
from helpers import check_directory_permission


class ReadFile(Tool):
    name = "ReadFile"
    description = '''
      Returns the contents of a file.
      Useful when you want to learn about the contents of a file.
      Useful when you need to understand the user's code. 
      `file_path` should be a string with the path to a single file.
    '''

    def _run(self, file_path: str) -> str:
        """Use the tool."""
        if file_path:
            dir_allowed, normalized_file_path = check_directory_permission(
                file_path, self.settings)
            if dir_allowed:
                with open(normalized_file_path, 'r') as f:
                    contents = f.read()
                return contents
            else:
                return "ERROR: Reading a file outside of the working_directory is not allowed."
        else:
            return "ERROR: Couldn't read a file. No path provided."