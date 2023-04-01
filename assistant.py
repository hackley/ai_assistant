import os
import datetime
import pyaudio
import wave
import openai
import requests
import json
import webrtcvad
import numpy as np
import re
from dotenv import load_dotenv
import importlib
import sys
from pathlib import Path
import argparse


MODEL = "gpt-4"

# Dynamically import action modules
actions_path = Path('actions')
sys.path.insert(0, str(actions_path.resolve()))
action_modules = []
ACTION_DESCRIPTIONS = []

for action_file in actions_path.glob('*.py'):
  if action_file.stem != '__init__':
    module_name = action_file.stem
    action_module = importlib.import_module(module_name)
    action_modules.append(action_module)
    ACTION_DESCRIPTIONS.append(action_module.description)



load_dotenv()  # Load environment variables from .env file

# Get the value of OPENAI_API_KEY from the environment
api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = api_key

# Set up audio parameters
RATE = 16000
CHUNK = int(RATE * 0.03)  # 30 ms frame duration
FORMAT = pyaudio.paInt16
CHANNELS = 1
WAVE_OUTPUT_FILENAME = "tmp/audio.wav"
RECORDING_PAUSE_DURATION_CHUNKS = 30

# Set up VAD
VAD_MODE = 3
vad = webrtcvad.Vad(VAD_MODE)


def format_action_descriptions(action_descriptions):
  formatted_descriptions = []
  for desc in action_descriptions:
    action_str = f"- {desc['action']}: {desc['description']}\n"
    args_str = "\n".join([f"  - {k}: {v}" for k, v in desc['arguments'].items()])
    formatted_descriptions.append(f"{action_str}  {args_str}\n")
  return "".join(formatted_descriptions)

INITIAL_PROMPT = f"""
You are a virtual assistant and code-writing partner. Your job is to listen to the user and respond with helpful information or, when the user asks you to, execute an action.
If you decide that the user is asking you to execute an action, you'll need to respond in a very specific format. Each action request should be wrapped in square brackets and include the name of the action and any arguments in parentheses. 
For example, if the user wants you to create a file, you'll need to respond with: "[create_file(file_name=myfile.txt)]", where "myfile.txt" is the name of the file you want to create. Do not include quotes around arguments.
Multiple actions can be triggered with a single response. Include them in the order you want them executed and put each action on it's own line. However, if you'd like to execute an action that requires a response from the user or system, you'll need to wait for a response before executing the next action.
The result of these actions will be returned to you in the order they were executed, in JSON format.
You have access to the following actions (arguments listed below each; you may only pass these arguments to the corresponding action, all others will be ignored; please follow the instructions shown for each argument): 
{format_action_descriptions(ACTION_DESCRIPTIONS)}
Please respond with "Let's get to work!" to begin.
"""

# TODO: ask the AI to always respond in JSON format. with a "response" key and an "actions" key. 
# actions is an array of hashes


def execute_action(action_name, args):
  module = importlib.import_module(f"actions.{action_name}")
  func = getattr(module, action_name)
  return func(args)

def parse_action_response(response):
  action_pattern = r'\[(?P<action>[a-z_]+)\((?P<args>[^\)]*)\)\]'
  matches = re.finditer(action_pattern, response)
  actions_with_args = []

  for match in matches:
    action = match.group('action')
    args_str = match.group('args')
    args_list = [arg.strip() for arg in args_str.split(',')]
    args = {}
    for arg in args_list:
      key, value = arg.split('=')
      args[key.strip()] = value.strip()
    actions_with_args.append((action, args))

  return actions_with_args


def record_audio():
  p = pyaudio.PyAudio()

  # Get the default input device index
  default_input_device_info = p.get_default_input_device_info()
  default_input_device_index = default_input_device_info["index"]

  stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    frames_per_buffer=CHUNK,
    input_device_index=default_input_device_index
  )

  print("Listening...")

  frames = []
  num_silent_chunks = 0
  speech_detected = False

  while True:
    data = stream.read(CHUNK)
    # Convert the data to a numpy array
    int_data = np.frombuffer(data, dtype=np.int16)
    # Pass the converted data to VAD
    is_speech = vad.is_speech(int_data.tobytes(), RATE)

    if not speech_detected:
      if is_speech:
        speech_detected = True
        print("Recording...")

    if speech_detected:
      frames.append(data)
      if is_speech:
        num_silent_chunks = 0
      else:
        num_silent_chunks += 1

      if num_silent_chunks > RECORDING_PAUSE_DURATION_CHUNKS:
        break

  print("Finished recording.")

  stream.stop_stream()
  stream.close()
  p.terminate()

  wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
  wf.setnchannels(CHANNELS)
  wf.setsampwidth(p.get_sample_size(FORMAT))
  wf.setframerate(RATE)
  wf.writeframes(b''.join(frames))
  wf.close()


def transcribe_audio():
  audio_file = open(WAVE_OUTPUT_FILENAME, "rb")
  transcript = openai.Audio.transcribe("whisper-1", audio_file)

  os.remove(WAVE_OUTPUT_FILENAME)
  return transcript.text


# where should we save the transcript?
transcript_file_name = (
    "transcripts/"
    + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    + "_transcript.jsonl"
)

messages = []

sender_options = {
  "system": "System",
  "user": "You",
  "assistant": "Assistant"
}


def commit_message(sender, text):
  message = {"role": sender, "content": text}
  messages.append(message)
  with open(transcript_file_name, "a") as f:
    f.write(json.dumps(message) + '\n')
  
  if sender != "user":
    print_message(sender, text)


def print_message(sender, text):
  sender_pretty = sender_options[sender]
  print(f'{sender_pretty}: {text}')


def send_message(sender, text):
  commit_message(sender, text)
  return chat_with_gpt(messages)


def chat_with_gpt(messages): 
  response = openai.ChatCompletion.create(
    model=MODEL,
    messages=messages 
  )
  reply = response.choices[0].message["content"]

  # For debuggin purposes. Maybe make this off by default at some point.
  with open('tmp/last_request.json', "a") as f:
    messages_hash = {"messages": messages}
    f.write(json.dumps(messages_hash))

  formatted_reply = reply.strip()
  commit_message("assistant", formatted_reply)

  actions_with_args = parse_action_response(formatted_reply)
  if actions_with_args:
    results = []
    for action_name, args in actions_with_args:
      res = execute_action(action_name, args)
      results.append([action_name, res])
    system_reply = formatted_action_results(results)
    send_message('system', system_reply)

  return True


def formatted_action_results(results):
  formatted_result = "Here are the results of your actions, in JSON format:\n"
  for index, (action_name, result) in enumerate(results, start=1):
    formatted_result += f'{{order: {index}, action: "{action_name}", result: "{result}"}}\n'
  return formatted_result

def parse_arguments(): 
  parser = argparse.ArgumentParser(
    description="Voice-activated GPT assistant")
  parser.add_argument(
    "--voice-mode",
    action="store_true",
    help="Use voice mode instead of text mode (default: False)",
  )
  args = parser.parse_args()
  return args.voice_mode


def main(mode):

  send_message("system", INITIAL_PROMPT)

  while True:
    if mode:  # Check if the mode is voice or text
      record_audio()
      text = transcribe_audio()
      print_message("user", text)
    else:
      text = input("You: ")

    if text:
      if text.lower() == "exit." or text.lower() == "exit":
        commit_message('user', text)
        commit_message('system', "Goodbye.")
        break

      send_message("user", text)
    else:
      print("Couldn't transcribe audio. Try again.")


if __name__ == "__main__":
  voice_mode = parse_arguments()
  main(voice_mode)
