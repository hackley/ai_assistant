import os
import sys
import importlib
from pathlib import Path
from dotenv import load_dotenv

from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent

from helpers import to_camel_case


load_dotenv()  # Load environment variables from .env file

# Get the value of OPENAI_API_KEY from the environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Config
EXIT_WORDS = ["exit", "exit."]

# Load Tools
tools_path = Path('tools')
sys.path.insert(0, str(tools_path.resolve()))
tools = []
for tool_file in tools_path.glob('*.py'):
  if tool_file.stem != '__init__':
    module_name = tool_file.stem
    klass_name = to_camel_case(module_name)
    tool_module = importlib.import_module(module_name)
    klass = getattr(tool_module, klass_name)
    tools.append(klass())
print("Tools:", tools)

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
