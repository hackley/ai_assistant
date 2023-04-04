import os
from langchain.tools import BaseTool


class WriteToFile(BaseTool):
    name = "WriteToFile"
    description = '''
      This action replaces the contents of a file and returns 'true' if successful.
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

    async def _arun(self, file_path: str) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("WriteToFile does not support async")
