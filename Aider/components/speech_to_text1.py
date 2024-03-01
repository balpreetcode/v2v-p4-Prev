import os
import asyncio
import json
import pyaudio
import websockets
from dotenv import load_dotenv
import pyautogui as pg  # Ensure pyautogui is imported

# Load environment variables from .env file for secure access
load_dotenv()

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 8000

class Transcriber:
    def __init__(self):
        self.audio_queue = asyncio.Queue()
        self.stream = None  # Placeholder for the PyAudio stream
        self.stop_pushing = False  # Flag to stop pushing data to the queue

    def mic_callback(self, input_data, frame_count, time_info, status_flag):
        if not self.stop_pushing:
            self.audio_queue.put_nowait(input_data)
        return (input_data, pyaudio.paContinue)

    async def sender(self, ws, timeout=0.1):
        """Send audio data from the microphone to Deepgram."""
        try:
            while not self.stop_pushing:
                mic_data = await asyncio.wait_for(self.audio_queue.get(), timeout)
                await ws.send(mic_data)
        except asyncio.TimeoutError:
            print("Timeout in sender coroutine. Stopping the push.")
        except websockets.exceptions.ConnectionClosedError as e:
            print(f"WebSocket connection closed unexpectedly in sender: {e}")
        finally:
            self.stop_pushing = True

    async def receiver(self, ws):
        """Receive transcription results from Deepgram."""
        try:
            async for msg in ws:
                res = json.loads(msg)
                if res.get("is_final"):
                    transcript = (
                        res.get("channel", {})
                        .get("alternatives", [{}])[0]
                        .get("transcript", "")
                    )
                    if transcript.strip():
                        return transcript
        except asyncio.TimeoutError:
            print("Timeout occurred in receiver coroutine.")
        except websockets.exceptions.ConnectionClosedError as e:
            print(f"WebSocket connection closed unexpectedly in receiver: {e}")
        finally:
            if ws.open:
                await ws.close()

    def check_call_end(self):
        """Check for the call end button."""
        end_call = pg.locateOnScreen("assets/buttons/end_call.png", confidence=0.98)
        if end_call:
            print("Call ended")
            self.stop_pushing = True

    async def check_call_end_periodically(self, check_interval=1):
        """Periodically check for the call end button."""
        while not self.stop_pushing:
            self.check_call_end()
            await asyncio.sleep(check_interval)

    async def run(self, key):
        deepgram_url = f"wss://api.deepgram.com/v1/listen?punctuate=true&encoding=linear16&sample_rate=16000"
        
        # Open the microphone stream
        p = pyaudio.PyAudio()
        self.stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, stream_callback=self.mic_callback)
        self.stream.start_stream()

        try:
            async with websockets.connect(
                deepgram_url, 
                extra_headers={"Authorization": f"Token {key}"}, 
                timeout=0.3
            ) as ws:

                sender_coroutine = self.sender(ws)
                receiver_coroutine = self.receiver(ws)
                call_end_check_task = asyncio.create_task(self.check_call_end_periodically())

                results = await asyncio.gather(sender_coroutine, receiver_coroutine, call_end_check_task, return_exceptions=True)
                
                transcript = next((r for r in results if isinstance(r, str)), None)
                return transcript

        except Exception as e:
            print(f"Error during transcription: {e}")
            return None

        finally:
            # Ensure resources are released
            if self.stream.is_active():
                self.stream.stop_stream()
            self.stream.close()
            p.terminate()

def transcribe_stream():
    DEEPGRAM_API_KEY = os.getenv('DEEPGRAM_API_KEY')
    if DEEPGRAM_API_KEY is None:
        print("Please set the DEEPGRAM_API_KEY environment variable.")
        return

    print("Start speaking...")
    transcriber = Transcriber()
    
    loop = asyncio.get_event_loop()  # Use an existing loop if available, otherwise create a new one
    transcript = loop.run_until_complete(transcriber.run(DEEPGRAM_API_KEY))
    return transcript
