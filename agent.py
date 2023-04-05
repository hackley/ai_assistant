import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import json

from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent
from langchain import PromptTemplate

from helpers import init_tool
from chat_history import ChatMessageHistory


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


model = ChatOpenAI(temperature=0.8, model_name="gpt-4")

template = '''
  You are a virtual assistant and code-writing partner that has been hired by the user to help with some programing projects. Your job is to help the user by answering questions and performing tasks with your tools.
  If you run into roadblocks, you can ask the user for more information. But you should always try to complete the task at hand, even if it takes a few tries or approaches.
  {chat_history}
  Human: {question}
  AI:
'''

prompt = PromptTemplate(
    input_variables=["chat_history", "question"], 
    template=template)



def run_agent(session_id, user_input):
  print(prompt)
  message_history = ChatMessageHistory(session_id=session_id)
  memory = ConversationBufferMemory(
      memory_key="chat_history",
      chat_memory=message_history,
      return_messages=True)
  agent_chain = initialize_agent(
      llm=model,
      prompt=prompt,
      tools=tools,
      memory=memory,
      agent="chat-conversational-react-description",
      verbose=True)
  response = agent_chain.run(user_input)
  message_history.connection.close()
  return response
