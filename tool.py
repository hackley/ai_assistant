from langchain.tools import BaseTool
from pydantic import Field


class CustomBaseTool(BaseTool):
    settings: dict = Field({}, description="Tool settings")


class Tool(CustomBaseTool):
    name = "UNDEFINED"
    description = "UNDEFINED"

    def __init__(self, settings: dict = {}):
        super().__init__(settings=settings)

    def _run(self, args: dict) -> str:
        """Use the tool."""
        return "true"

    async def _arun(self, file_path: str) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("Tool does not support async")
