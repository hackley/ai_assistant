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

# actions
from actions.create_file import create_file

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

INITIAL_PROMPT = """
You are a virtual assistant and code-writing partner. Your job is to listen to the user and respond with helpful information or, when the user asks you to, execute an action.
If you decide that the user is asking you to execute an action, you'll need to respond in a very specific format that includes the name of the action and any parameters that are required to execute it. 
For example, if the user wants you to create a file, you'll need to respond with: "[create_file(file_name=myfile.txt)]", where "myfile.txt" is the name of the file you want to create. 
You have access to the following actions (arguments listed below each): 
- create_file: Creates a file with the given name.
  - file_name: The name of the file to create.
"""


def execute_action(action, args):
  print(f"Executing action: {action}({args})")
  if action == 'create_file':
    return create_file(args)
  else:
    return f"Unknown action: {action}"


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


def chat_with_gpt(text):
  messages = [
    {"role": "system", "content": INITIAL_PROMPT},
    {"role": "user", "content": text}
  ]

  response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=messages
  )
  reply = response.choices[0].message['content']

  return reply.strip()


def main():
  transcript_file_name = 'tmp/' + \
    datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '_transcript.jsonl'

  while True:
    record_audio()
    text = transcribe_audio()
    if text:
      print(f'You: {text}')
      user_message = {"role": "user", "content": text}
      with open(transcript_file_name, 'a') as f:
        f.write(json.dumps(user_message) + '\n')

      if text.lower() == "exit.":
        print("Exiting the conversation.")
        break

      response = chat_with_gpt(text)
      actions_with_args = parse_action_response(response)

      if actions_with_args:
        print(f'ChatGPT: {response}')
        chatgpt_message = {"role": "ChatGPT", "content": response}
        with open(transcript_file_name, 'a') as f:
          f.write(json.dumps(chatgpt_message) + '\n')

        for action, args in actions_with_args:
          action_result = execute_action(action, args)
          print(f'System: {action_result}')
          system_message = {"role": "system", "content": action_result}
          with open(transcript_file_name, 'a') as f:
            f.write(json.dumps(system_message) + '\n')
      else:
        print(f'ChatGPT: {response}')
        chatgpt_message = {"role": "ChatGPT", "content": response}
        with open(transcript_file_name, 'a') as f:
          f.write(json.dumps(chatgpt_message) + '\n')
    else:
      print("Couldn't transcribe audio. Try again.")



if __name__ == '__main__':
  main()
