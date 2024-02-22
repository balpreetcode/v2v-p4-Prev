from pyht import Client
from dotenv import load_dotenv
import numpy as np
import sounddevice as sd
import soundfile as sf
from pyht.client import TTSOptions
import time  # Import the time module
import os
load_dotenv()

client = Client(
    user_id=os.getenv("PLAYHT_USER_ID"),
    api_key=os.getenv("PLAYHT_API_KEY"),
 )
options = TTSOptions(voice="s3://voice-cloning-zero-shot/d9ff78ba-d016-47f6-b0ef-dd630f59414e/female-cs/manifest.json")
sample_rate = 20000
initial_chunks_to_buffer = 1  # Adjust based on your chunk size and desired latency
buffer = []

stream = sd.OutputStream(samplerate=sample_rate, channels=1, dtype='float32')  # Ensure dtype is set to 'float32'
stream.start()

# Variable to store the start time
start_time = None

# Variable to check if the first audio play has happened
first_audio_played = False

# Function to handle playback of each chunk
def play_chunk(chunk, start_time, first_audio_played):
    # Convert byte data to NumPy array with 'int16' dtype and then to 'float32'
    audio_data = np.frombuffer(chunk, dtype=np.int16).astype(np.float32) / np.iinfo(np.int16).max
    
    # If initial buffer is not yet full, add the chunk to the buffer
    if len(buffer) < initial_chunks_to_buffer:
        buffer.append(audio_data)
        if len(buffer) == initial_chunks_to_buffer:
            # Once buffer is full, concatenate buffered chunks
            initial_data = np.concatenate(buffer)
            # Capture the timestamp just before playing
            play_time = time.time()
            # Calculate the time difference
            time_diff = play_time - start_time
            print(f"Time from tts call to first play: {time_diff} seconds")
            # Write the initial data to the stream and play
            stream.write(initial_data)
            first_audio_played = True
    else:
        # For subsequent chunks, write directly to the stream
        stream.write(audio_data)

    return first_audio_played

# Capture the start time before calling the tts function
start_time = time.time()

# Example usage with your TTS client
for chunk in client.tts("Can you tell me your account email or, ah your phone number?", options):
    if not first_audio_played:
        first_audio_played = play_chunk(chunk, start_time, first_audio_played)
    else:
        play_chunk(chunk, start_time, first_audio_played)

# Cleanup: Stop and close the stream when done
stream.stop()
stream.close()
