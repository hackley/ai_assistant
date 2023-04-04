import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import json

from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent

from helpers import init_tool


load_dotenv()  # Load environment variables from .env file

# Get the value of OPENAI_API_KEY from the environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


# Load Settings
settings_path = Path('settings.json')
with open(settings_path, 'r') as f:
    settings = json.load(f)


# Load Tools
tools_path = Path('tools')
sys.path.insert(0, str(tools_path.resolve()))
tools = []
for tool_file in tools_path.glob('*.py'):
    if tool_file.stem != '__init__':
        tool = init_tool(tool_file, settings)
        if tool is not None:
            tools.append(tool)


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
    if user_input.lower() in settings['exit_words']:
        print("System: Goodbye.")
        break
    response = agent_chain.run(user_input)
    print("Agent: ", response)
