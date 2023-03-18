import os
import datetime
import pyaudio
import wave
import openai
import requests
import json
import webrtcvad
import numpy as np
from dotenv import load_dotenv


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
RECORDING_PAUSE_DURATION_CHUNKS = 60

# Set up VAD
VAD_MODE = 3
vad = webrtcvad.Vad(VAD_MODE)


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
        {"role": "system", "content": "You are chatting with ChatGPT."},
        {"role": "user", "content": text}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=messages
    )
    reply = response.choices[0].message['content']

    return reply.strip()


def main():
    transcript_file_name = 'tmp/' + datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '_transcript.txt'

    while True:
        record_audio()
        text = transcribe_audio()
        if text:
            print(f'You: {text}')
            with open(transcript_file_name, 'a') as f:
                f.write(f'You: {text}\n')

            if text.lower() == "exit.":
                print("Exiting the conversation.")
                break

            response = chat_with_gpt(text)
            print(f'ChatGPT: {response}')
            with open(transcript_file_name, 'a') as f:
                f.write(f'ChatGPT: {response}\n')
        else:
            print("Couldn't transcribe audio. Try again.")


if __name__ == '__main__':
    main()
