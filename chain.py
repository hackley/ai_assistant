import os
from dotenv import load_dotenv

from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent
from langchain.tools import BaseTool

load_dotenv()  # Load environment variables from .env file

# Get the value of OPENAI_API_KEY from the environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


# Config
EXIT_WORDS = ["exit", "exit."]

# TODO: convert actions folder to use this format
class CreateFile(BaseTool):
    name = "Create File"
    description = "Create a file at a given path."

    def _run(self, file_path: str) -> str:
        """Use the tool."""
        with open(f"tmp/project/{file_path}", 'w') as f:
            f.write('')
        return f"Created a file at '{file_path}'."

    async def _arun(self, file_path: str) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("CreateFile does not support async")

tools = [
    CreateFile()
]

memory = ConversationBufferMemory(
    memory_key="chat_history", 
    return_messages=True)

llm = ChatOpenAI(temperature=0, model_name="gpt-4")

agent_chain = initialize_agent(
    tools, 
    llm, 
    agent="chat-conversational-react-description", 
    verbose=True, 
    memory=memory)

while True:
    user_input = input("You: ")
    if user_input.lower() in EXIT_WORDS:
        print("System: Goodbye.")
        break
    response = agent_chain.run(user_input)
    print("Agent: ", response)
