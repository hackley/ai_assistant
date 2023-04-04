import os
from tool import Tool

class CreateFile(Tool):
    name = "CreateFile"
    description = "Create a file at a given path."

    def working_directory(self) -> str:
        """Return the working directory."""
        return self.settings["working_directory"]

    def _run(self, file_path: str) -> str:
        """Use the tool."""
        if file_path:
            directory = self.working_directory()
            full_file_path = os.path.join(directory, file_path)
            normalized_file_path = os.path.normpath(os.path.abspath(full_file_path))

            if normalized_file_path.startswith(directory):
                with open(normalized_file_path, 'w') as f:
                    f.write('')
                return f"Created a file at '{normalized_file_path}'."
            else:
                return "ERROR: Creating a file outside of the working_directory is not allowed."
        else:
           return "ERROR: Couldn't create a file. No path provided."

