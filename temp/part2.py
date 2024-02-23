# mix

import json
import soundfile as sf
import sounddevice as sd
import pplx_playht_final
# import faiss_code
# from faiss_code import get_faiss_response

# Path to your JSON file
filename = 'data.json'

# Load JSON data from the file
with open(filename, 'r') as file:
    data = json.load(file)


def fetch_sub_category(category):

    with open('data.json', 'r') as file:
        data = json.load(file)

    # Convert the category_json string to a Python dictionary
    category_info = json.loads(category[0])

    # Filter the data based on the given category
    filtered_data = [entry for entry in data if entry["Category"] == category_info["Category"]]

    # Prepare the result JSON
    result = []
    for item in filtered_data:
        result.append({
            "Category": item["Category"],
            "Sub Category": item["Sub Category"],
            "Sub Sub Category": item["Sub Sub Category"]
        })

    # Convert the result to JSON string
    result_json = json.dumps(result, indent=4)

    print(result_json)
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
                Which category, sub category and sub sub category does this user query belong to?
                Always respond in json format {"Category": "<category>", "Sub Category": "<subCategory>", "Sub Sub Category": "<subSubCategory>"}
                ''' + str(sub_category) 
                # '''
                # Which category, sub category and sub sub category does this user query belong to?
                # Always respond in json format {"Category": "<category>", "Sub Category": "<subCategory>", "Sub Sub Category": "<subSubCategory>"}
                # ''' + str(sub_category) 
            ),
        }
    ]

    # query = input('user:')
    # print(query)
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
            # new_content = content.replace(processed_content, "", 1).strip()  # Remove already processed content
            # print(content)

    if content.strip():
        messages.append({"role": "assistant", "content": content.strip()})
        print('final answer:', content.strip())

    return content

################################################################################

# The pattern to search for
def response_type(query, category, chat_history):
    # FAQ = '{"Category": "FAQs"}'
    FAQ = '"Category": "FAQs"'

    filename = 'letmecheck.wav'  # Replace with the path to your audio file
    d, fs = sf.read(filename)

    
    # Check if the pattern is in the string
    if FAQ in category:
        print("yes")     ## run faiss code
        # get_faiss_response(query)
    else:
        print("no")   # run fetch data.py
        #Play the audio file
        sd.play(d, fs)
        # sd.wait() 
        category = str(category[0])
        sub_category = fetch_sub_category(category)
        print('sub_category:', sub_category)
        # info = find_information(data, sub_category)
        sub_category = json.loads(sub_category)

        final_sub_sub_category_ = final_sub_sub_category(sub_category, query)
        print('final_sub_sub_category:', final_sub_sub_category_)
        final_sub_sub_category_ = json.loads(final_sub_sub_category_)
        info = find_information(data, final_sub_sub_category_)
        print(info)
        chat_history = pplx_playht_final.final_answer(info, chat_history, query)
        # info = find_information_all(data, sub_category)

    return chat_history



# import streaming_audio
# chat_history = []

# query = 'I have some issues with payment'
# category =['{"Category": "Billing"}']
# info = response_type(query, category)

# # print(info)

# answer = streaming_audio.final_answer(info, chat_history, query)
# # print(answer)
