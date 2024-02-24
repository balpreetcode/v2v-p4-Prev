
import openai
from dotenv import load_dotenv
import os
import re

# Load environment variables from .env file
load_dotenv()

# Access environment variables
PPLX_API_KEY = os.environ.get("PPLX_API_KEY")
os.environ["PPLX_API_KEY"] = PPLX_API_KEY

model_name="llama-2-70b-chat"

def get_category(query):
    messages = [
        {
            "role": "system",
            "content": (
                '''You are a Hotel receptionist who provides responses to customer queries
                Respond with a Question category as json format {"category":"<>"}. Values can be Billing, product Info, FAQs
                FAQ questions include "What is your name?", "Is this the Grand Holiday Hotel?", "Do you have room service?", "Do you have Wi-Fi?", "What's the checkout time?"
                This statement belongs to which sub category of product info? Available Rooms,Pricing, Amenities, Others?
                Always respond with following json format {"Category": "<category>", "SubCategory": "<subCategory>"}'''
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

        pattern = r'\{.*?\}'

        # Search for JSON-like strings
        matches = re.findall(pattern, content)
        print(matches)

    # return content
    return matches