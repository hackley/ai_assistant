import os
from tool import Tool


class ReadFile(Tool):
    name = "ReadFile"
    description = "Reads a file and returns its contents."

    def _run(self, file_path: str) -> str:
        """Use the tool."""
        if file_path is not None:
            try:
                with open(file_path, 'r') as file:
                  content = file.read()
                  return content
            except Exception as e:
                return f"ERROR: {e}"
        else:
            return f"ERROR: No path provided."
