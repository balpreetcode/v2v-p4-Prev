import json
import soundfile as sf
import sounddevice as sd
import pplx_playht_final
import prompt_response
import re

# Path to your JSON file
filename = 'data.json'

# Load JSON data from the file
with open(filename, 'r') as file:
    data = json.load(file)

def fetch_sub_category(category):
    try:
        with open('data.json', 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        print("File not found. Ensure 'data.json' exists in the correct path.")
        return {}
    # print('data:',data)
    # print('category:',category)
    # Filter the data based on both Category and Sub Category
    filtered_data = [entry for entry in data if entry["Category"] == category["Category"] and entry.get("Sub Category") == category.get("Sub Category")]
    # print('Filtered Data:', filtered_data)

    # If filtered_data is empty, use default values
    if not filtered_data:
        result_json = json.dumps({
            "Category": category.get("Category", "N/A"),
            "Sub Category": category.get("Sub Category", "N/A"),
            "Sub Sub Category": ""  # Assuming you want an empty string if no sub-sub-category exists
        }, indent=4)
    else:
        result = []
        for item in filtered_data:
            result.append({
                "Category": item["Category"],
                "Sub Category": item.get("Sub Category", "N/A"),
                "Sub Sub Category": item.get("Sub Sub Category", "N/A")
            })
        result_json = json.dumps(result, indent=4)

    print('Result JSON:', result_json)
    return result_json

def find_information_all(data, criteria_list):
    results = []
    for criteria in criteria_list:
        # Ensure criteria is a dictionary
        if isinstance(criteria, dict):
            match_found = False
            for item in data:
                if all(item.get(key) == value for key, value in criteria.items()):
                    results.append(item.get("Information", "Information not found"))
                    match_found = True
                    break
            if not match_found:
                results.append("Information not found")
        else:
            print("Error: criteria is not a dictionary", criteria)
    return results

def find_information(data, criteria):
    for item in data:
        if all(item[key] == value for key, value in criteria.items()):
            return item.get("Information")  # Return the matching information
    return "Information not found"  # Return a default message if no match is found
#############################################################################3

import openai
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Access environment variables
PPLX_API_KEY = os.environ.get("PPLX_API_KEY")
os.environ["PPLX_API_KEY"] = PPLX_API_KEY

model_name="llama-2-70b-chat"

def final_sub_sub_category(sub_category, query):
    messages = [
        {
            "role": "system",
            "content": (

                '''
                Which category, sub category and sub sub category does this user query belong to from the given options?
                Always respond in json format {"Category": "<category>", "Sub Category": "<subCategory>", "Sub Sub Category": "<subSubCategory>"}.
                Options: 
                ''' +  str(sub_category) 
                
            ),
        }
    ]

    messages.append({"role": "user", "content": f'user query: {query}'})


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
            

    if content.strip():
        pattern = r'\{.*?\}'
        
        matches = re.findall(pattern, content, re.DOTALL)
        matches = json.loads(matches[0])
        print('matches: ',matches)
        return matches

    return str(matches)  #[], content

################################################################################

# The pattern to search for
def response_type(query, category, type_value, chat_history):
   
    if type_value == '1':
        print("General Inquiry")     
        chat_history = prompt_response.play_prompt_response(chat_history, query)

    else:
        print("Account Specific Inquiry")   
        sub_category = fetch_sub_category(category)
        print('sub_category:', sub_category)
        # info = find_information(data, sub_category)
        sub_category = json.loads(sub_category)

        final_sub_sub_category_ = final_sub_sub_category(sub_category, query)
        print('final_sub_sub_category:', final_sub_sub_category_)
        # final_sub_sub_category_ = json.loads(final_sub_sub_category_)
        info = find_information(data, final_sub_sub_category_)
        print(info)
        chat_history = pplx_playht_final.final_answer(info, chat_history, query)
        # info = find_information_all(data, sub_category)

    return chat_history

