import os
from tool import Tool
from helpers import check_directory_permission


class CreateDirectory(Tool):
    name = "CreateDirectory"
    description = "Creates a new directory. Can be nested."

    def _run(self, dir_path: str) -> str:
        """Use the tool."""
        if dir_path:
            dir_allowed, normalized_dir_path = check_directory_permission(
                dir_path, self.settings)
            if dir_allowed:
                os.makedirs(normalized_dir_path)
                return f"Created a directory at '{normalized_dir_path}'."
            else:
                return "ERROR: Creating a file outside of the working_directory is not allowed."
        else:
           return "ERROR: Couldn't create a file. No path provided."
