import os
from langchain.tools import BaseTool

working_directory = "/Users/nathan/Code/assistant/tmp/project"

class CreateFile(BaseTool):
    name = "CreateFile"
    description = "Create a file at a given path."

    def _run(self, file_path: str) -> str:
        """Use the tool."""
        if file_path:
            full_file_path = os.path.join(working_directory, file_path)
            normalized_file_path = os.path.normpath(os.path.abspath(full_file_path))

            if normalized_file_path.startswith(working_directory):
                with open(normalized_file_path, 'w') as f:
                    f.write('')
                return f"Created a file at '{normalized_file_path}'."
            else:
                return "ERROR: Creating a file outside of the working_directory is not allowed."
        else:
           return "ERROR: Couldn't create a file. No path provided."


    async def _arun(self, file_path: str) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("CreateFile does not support async")
