
import os
import uuid
import datetime
import openai
from dotenv import load_dotenv
import numpy as np
import faiss
import sys
from sklearn.feature_extraction.text import TfidfVectorizer
import sounddevice as sd
import wavio
import re
import time
import pyautogui as pg
import webbrowser
import soundfile as sf
import threading
from queue import Queue

# Load environment variables from .env file
load_dotenv()

# Access environment variables
PPLX_API_KEY = os.environ.get("PPLX_API_KEY")
os.environ["PPLX_API_KEY"] = PPLX_API_KEY

model_name="llama-2-70b-chat"

sys.path.append("./components")
sys.path.append("./constants")
# import speech_to_text1
# from filler_mapping import classify_and_play_audio, refresh_learning_data
from dictionary import phrases_dict

def generate_unique_id():
    return str(uuid.uuid4())

conversation_id = generate_unique_id()

# 1. FAISS Indexing
# Convert phrases to embeddings for searching
vectorizer = TfidfVectorizer().fit(phrases_dict.keys())
phrases_embeddings = vectorizer.transform(phrases_dict.keys())
index = faiss.IndexIDMap(faiss.IndexFlatIP(phrases_embeddings.shape[1]))
index.add_with_ids(np.array(phrases_embeddings.toarray(), dtype=np.float32), np.array(list(range(len(phrases_dict)))))

def find_matching_audio(sentence):
    start_time_f = datetime.datetime.now()
    # print(f'Phrase given to faiss {start_time_f}')
    # Convert the sentence to embedding and search in the index
    sentence_embedding = vectorizer.transform([sentence]).toarray().astype(np.float32)
    D, I = index.search(sentence_embedding, 1)
    match_index = I[0][0]
    matching_sentence = list(phrases_dict.keys())[match_index]

    if D[0][0] > 0.1:  # You can adjust this threshold based on desired accuracy
        return phrases_dict[matching_sentence]
    return None

processed_sentences = set()
audio_queue = Queue()
is_audio_playing = False

def audio_worker():
    global is_audio_playing
    while True:
        audio_data, samplerate = audio_queue.get()
        if audio_data is None:
            break  # This is the signal to stop the worker
        is_audio_playing = True
        sd.play(audio_data, samplerate)
        sd.wait()
        is_audio_playing = False
        audio_queue.task_done()


audio_thread = threading.Thread(target=audio_worker)
audio_thread.start()


def preload_audio_files():
    for file in os.listdir("./assets/audio_files_pixel"):
        if file.endswith(".wav"):
            audio_code = file.split('.')[0]
            audio_path = f"./assets/audio_files_pixel/{file}"
            data, samplerate = sf.read(audio_path)
            preloaded_audio[audio_code] = (data, samplerate)

# Global dictionary to hold preloaded audio data
preloaded_audio = {}
preload_audio_files()

def play_audio_in_thread(audio_data, samplerate):
    sd.play(audio_data, samplerate)
    sd.wait()

def handle_gpt_response(full_content):
    sentences = re.split(r'[.!?]', full_content)
    sentences = [s.strip() for s in sentences if s]

    for sentence in sentences:
        if sentence not in processed_sentences:
            audio_code = find_matching_audio(sentence)
            print(f'sentence sent to faiss : {sentence}')
            if audio_code:
                audio_data, samplerate = preloaded_audio.get(audio_code, (None, None))
                if audio_data is not None:
                    audio_queue.put((audio_data, samplerate))
            processed_sentences.add(sentence)


def get_faiss_response(query):
    messages = [
        {
            "role": "system",
            "content": (
                "RESPOND WITH A VERY SHORT ANSWER. You are a receptionist named Jacob. Your task is to give demo about the academy to the user who is calling you and answer their queries based on the following information:" 
                "Following is a weekly schedule for Fight Flow Academy, which includes classes for MMA, boxing, and fitness:"
                "Monday to Friday at 6:15 AM: Boxing Bootcamp with Aileen. Kickboxing Bootcamp also appears on some days."
                "Saturday: HIIT Boxing at 8:00 AM and Muay Thai at 9:00 AM with Aileen."
                "Sunday: Muay Thai at 4:30 PM with Daison, and Jiu Jitsu (Gi) at 6 PM with Scott."
                "Evenings throughout the week at 5:30 PM: Various classes, including Youth Boxing/Kickboxing, Muay Thai, and MMA/MT Sparring."
                "Evening classes at 6:30 PM and 7:30 PM: Boxing Bootcamp, Muay Thai, Kickboxing Bootcamp, and Boxing Technique with instructors Sean, Johnny K, Tanner, Hung, and Daniel."
                "Our classes cater to all levels, from beginners to advanced practitioners, ensuring a safe and constructive learning environment. Empower yourself today at Fight Flow Academy in Raleigh!"
                "If the user asks how to register, tell them that you will send the details through SMS and inform them that there is one time registration fees of 50 dollars. If the user shows interest in joining, ask them if they would like to register. If yes, ask for their contact information. If no, thank them for their time."
                "End of the conversation: Have a great day!"
                "The address of Fight Flow Academy is: 900 E Six Forks Road, Raleigh, North Carolina."
                "You are having a conversation. Only respond to the last query in 2 or 3 sentences."
            ),
        }
    ]
    processed_content = ""

    sentence_end_pattern = re.compile(r'(?<=[.?!])\s')
    global is_audio_playing

    # while True:
    end_call = pg.locateOnScreen("assets/buttons/end_call.png", confidence = 0.98)  # path to your end call button image
    if end_call:
        print("Call ended")
        # break
        return
    # query = input('user: ')
    while is_audio_playing:
        time.sleep(0.1)
        
    # query = speech_to_text1.transcribe_stream()
    print(query)
    if query is None:  # Check if the transcription was interrupted
        print("Exiting chat due to call end.")
        # break
        return
    if query.lower() == "exit":
        # break
        return

    messages.append({"role": "user", "content": query})

    # Chat completion with streaming
    response_stream = openai.ChatCompletion.create(
        model=model_name,
        messages=messages,
        api_base="https://api.perplexity.ai",
        api_key=PPLX_API_KEY,
        stream=True,
    )

    for response in response_stream:
        if 'choices' in response:
            content = response['choices'][0]['message']['content']
            new_content = content.replace(processed_content, "", 1).strip()  # Remove already processed content
            print(new_content)

            # Split the content by sentence-ending punctuations
            parts = sentence_end_pattern.split(new_content)

            # Process each part that ends with a sentence-ending punctuation
            for part in parts[:-1]:  # Exclude the last part for now
                part = part.strip()
                if part:
                    handle_gpt_response(part + '.')  # Re-add the punctuation for processing
                    processed_content += part + ' '  # Add the processed part to processed_content

            # Now handle the last part separately
            last_part = parts[-1].strip()
            if last_part:
                # If the last part ends with a punctuation, process it directly
                if sentence_end_pattern.search(last_part):
                    handle_gpt_response(last_part)
                    processed_content += last_part + ' '
                else:
                    # Otherwise, add it to the sentence buffer to process it later
                    processed_content += last_part + ' '
    if last_part:
        print(f"Processed part sent to FAISS: '{last_part}'")
        handle_gpt_response(last_part)
        processed_content += last_part + ' '

    # Append only the complete assistant's response to messages
    if content.strip():
        messages.append({"role": "assistant", "content": content.strip()})

def cleanup():
    # Signal the audio worker to stop and wait for it to finish
    audio_queue.put((None, None))
    audio_thread.join()
    print("Audio worker stopped.")

# def open_website(url):
#         webbrowser.open(url, new=2)  # new=2 opens in a new tab, if possible

# Opening call hipppo dialer
#website = 'https://dialer.callhippo.com/dial'
#open_website(website)

#time.sleep(15)
#try:           
#    chat_with_user()       
#except KeyboardInterrupt:
#    print("Program interrupted by user. Cleaning up...")
#    cleanup()

# # Opening call hipppo dialer
# website = 'https://dialer.callhippo.com/dial'
# #open_website(website)

# #time.sleep(15)
            
# while True:  # Main loop for handling incoming calls
#     accept = pg.locateOnScreen("assets/buttons/accept.png", confidence=0.9)
#     if accept:
#         x, y, width, height = accept
#         click_x, click_y = x + width // 2, y + height // 2  # Calculate the center of the button
#         print("Call received at coordinates:", (click_x, click_y))
#         pg.moveTo(click_x, click_y)  # Move to the center of the button
#         time.sleep(0.5)  # Short delay
#         pg.mouseDown()
#         time.sleep(0.1)  # Short delay to simulate a real click
#         pg.mouseUp()
#         print("Call accepted")
#         chat_with_user()  # Start chat with user

#         print("Waiting for next call...")
#         time.sleep(5)
#     else:
#         print("No call detected.")
#         time.sleep(5) 
