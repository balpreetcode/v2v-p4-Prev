import sys
sys.path.append('./components')
import json
import speech_to_text1
import part2
from async_llama2 import llama_get_category
from playFiles import playAudioFile
import csv2json
import webbrowser
import pyautogui as pg
import time

# csv2json.convert_csv_to_json('data.csv')

def chat_with_user():
    chat_history = []
    while True:
        # query = speech_to_text1.transcribe_stream()
        query = 'I have some issues with payment'
        # query = 'What is the checkout time'
        # print('temp')
        category_filler = llama_get_category(query)
        type_value, filler_no,Category,Sub_Category=playAudioFile(category_filler)
        print('category_filler:' , category_filler)
        print('type_value:', type_value)
        print('filler_no:', filler_no)
        print('Category:', Category)
        print('Sub_Category:', Sub_Category)

        category = {
            'Category': Category,
            'Sub Category': Sub_Category
        }


        chat_history = part2.response_type(query, category, type_value, chat_history)


def open_website(url):
        webbrowser.open(url, new=2)  # new=2 opens in a new tab, if possible

# Opening call hipppo dialer
website = 'https://dialer.callhippo.com/dial'
            
while True:  # Main loop for handling incoming calls
    accept = pg.locateOnScreen("assets/buttons/accept.png", confidence=0.9)
    if accept:
        x, y, width, height = accept
        click_x, click_y = x + width // 2, y + height // 2  # Calculate the center of the button
        print("Call received at coordinates:", (click_x, click_y))
        pg.moveTo(click_x, click_y)  # Move to the center of the button
        time.sleep(0.5)  # Short delay
        pg.mouseDown()
        time.sleep(0.1)  # Short delay to simulate a real click
        pg.mouseUp()
        print("Call accepted")
        chat_with_user()  # Start chat with user

        print("Waiting for next call...")
        time.sleep(5)
    else:
        print("No call detected.")
        time.sleep(5) 