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


# Load the prompt
with open('system_prompt.txt', 'r') as file:
  prompt_content = file.read()

INITIAL_PROMPT = f"""
{prompt_content}
{format_action_descriptions(ACTION_DESCRIPTIONS)}\n
Please respond with "Let's get to work!" to begin.
"""

# TODO: ask the AI to always respond in JSON format. with a "response" key and an "actions" key. 
# actions is an array of hashes


def execute_action(action_name, args):
  module = importlib.import_module(f"actions.{action_name}")
  func = getattr(module, action_name)
  return func(args)


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

def set_transcript_file_name(loaded_name=None):
  global transcript_file_name
  if loaded_name is None:
    transcript_file_name = (
        "transcripts/"
        + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        + "_transcript.jsonl"
    )
  else:
    transcript_file_name = loaded_name
  return transcript_file_name

messages = []

sender_options = {
  "system": "System",
  "user": "You",
  "assistant": "Assistant"
}


def commit_message(sender, text, should_print=True):
  message = {"role": sender, "content": text}
  messages.append(message)
  with open(transcript_file_name, "a") as f:
    f.write(json.dumps(message) + '\n')
  
  if should_print:
    print_message(sender, text)


def print_message(sender, text):
  sender_pretty = sender_options[sender]
  print(f'{sender_pretty}: {text}')


def send_message(sender, text, should_print=True):
  commit_message(sender, text, should_print)
  return chat_with_gpt()


def process_reply_from_assistant(response_string):
  response = json.loads(response_string)

  if 'reply' in response:
    reply = response['reply']
    print_message('assistant', reply)

  if 'actions' in response:
    actions = response['actions']
    all_results = []
    for action in actions:
      action_name = action["action_name"]
      args = action["args"]
      result = execute_action(action_name, args)
      all_results.append((action_name, result))
    system_reply = formatted_action_results(all_results)
    send_message('system', system_reply, True)


def chat_with_gpt(): 
  request = openai.ChatCompletion.create(
    model=MODEL,
    messages=messages 
  )
  response_string = request.choices[0].message["content"].strip()
  commit_message("assistant", response_string, False)
  process_reply_from_assistant(response_string)
  return True


def formatted_action_results(results):
  system_response = {"action_results": results}
  return json.dumps(system_response)


def parse_arguments(): 
  parser = argparse.ArgumentParser(description="GPT coding assistant")
  parser.add_argument(
    "--voice-mode",
    action="store_true",
    help="Use voice mode instead of text mode (default: False)",
  )
  parser.add_argument(
    "--load-from",
    dest="load_from",
    default=None,
    help="Transcript file to boot from (default: None)"
  )
  return parser.parse_args()


def load_conversation():
  # load the transcript into memory
  with open(transcript_file_name, "r") as f:
    for line in f:
      message = json.loads(line)
      messages.append(message)

  # If the last message is from the assistant, then we should process it on our end.
  # If it's from the user or the system, then we should send the messages to the assistant.
  last_message = messages[-1]
  if last_message["role"] == "assistant":
    process_reply_from_assistant(last_message["content"])
  else:
    chat_with_gpt()


def main(options):
  if options.load_from:
    set_transcript_file_name(options.load_from)
    load_conversation()
  else:
    set_transcript_file_name()
    send_message("system", INITIAL_PROMPT)

  while True:
    if options.voice_mode:
      record_audio()
      text = transcribe_audio()
    else:
      text = input("You: ")

    if text:
      if text.lower() == "exit." or text.lower() == "exit":
        if options.voice_mode:
          print_message('user', text)
        print_message('system', "Goodbye.")
        break
      else:
        send_message("user", text, options.voice_mode)
    else:
      print("No input detected. Try again.")


if __name__ == "__main__":
  options = parse_arguments()
  main(options)
