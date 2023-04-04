from tool import Tool
from helpers import check_directory_permission

class CreateFile(Tool):
    name = "CreateFile"
    description = "Create a file at a given path."

    def _run(self, file_path: str) -> str:
        """Use the tool."""
        if file_path:
            dir_allowed, normalized_file_path = check_directory_permission(
                file_path, self.settings)
            if dir_allowed:
                with open(normalized_file_path, 'w') as f:
                    f.write('')
                return f"Created a file at '{normalized_file_path}'."
            else:
                return "ERROR: Creating a file outside of the working_directory is not allowed."
        else:
           return "ERROR: Couldn't create a file. No path provided."

