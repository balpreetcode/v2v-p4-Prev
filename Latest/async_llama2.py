import openai
from dotenv import load_dotenv
import os
import json

import re
from concurrent.futures import ThreadPoolExecutor, as_completed

# Load environment variables from .env file
load_dotenv()

# Access environment variables
PPLX_API_KEY = os.environ.get("PPLX_API_KEY")
os.environ["PPLX_API_KEY"] = PPLX_API_KEY

model_name="llama-2-70b-chat"

def get_category(query, system_message):
    messages = [
        {
            "role": "system",
            "content": system_message
        },
        {"role": "user", "content": f'user query: {query}'}
    ]

    # Chat completion with streaming
    response_stream = openai.ChatCompletion.create(
        model=model_name,
        messages=messages,
        api_base="https://api.perplexity.ai",
        api_key=PPLX_API_KEY,
        stream=True,
    )

    content = ""
    for response in response_stream:
        if 'choices' in response:
            content = response['choices'][0]['message']['content']
            # break  # Assuming we need just the first response that contains 'choices'

    if content.strip():
        pattern = r'\{.*?\}'
        
        matches = re.findall(pattern, content, re.DOTALL)
        
        return matches

    return [], content

prompt1=  '''You are Jacob, a Hotel receptionist who provides responses to customer queries.
                Respond with a Question category as json format {"category":"<>"}. Values can be Account Specific, General Inquiry.
                General Inquiry questions include "What is your name?", "Is this the Grand Holiday Hotel?", "Do you have room service?", "Do you have Wi-Fi?", "What's the checkout time?"
                Account Specific questions include these sub categories: Room Booking, Billing, Refunds, Feedback, Booking, Services.
                Always respond with following json format {"Category": "<category>", "Sub Category": "<subCategory>"} '''


prompt2 = '''"For detailed assistance on a wide range of topics, please refer to the appropriate Type:

- Type 1: This Type covers general inquiries and frequently asked questions including check-in and check-out procedures, availability and access to Wi-Fi, parking facilities, options for storing luggage before check-in or after check-out, breakfast inclusions with your stay, details about hotel amenities such as fitness centers, swimming pools, and spas, requests for extra bedding or cribs, pet accommodation policies, availability of accessible rooms for guests with disabilities, assistance with Wi-Fi connectivity issues, arranging transportation to and from the airport, exploring dining options within the hotel, recommendations for local restaurants, guidelines for modifying or canceling your booking, using the hotel's laundry services, the availability and operation of in-room safes, recommendations for local attractions and sightseeing, information on the hotel's meeting and event facilities, making special requests for your stay, and the hotel's smoking policy.

- Type 2: This Type is designated for inquiries that require access to external APIs or specific account details to provide a resolution. It includes checking the current availability of rooms for specific dates, requesting invoices to be sent via email for completed stays, reviewing detailed billing information for your stay, inquiring about the status of a refund for cancellations or service adjustments, and the process for logging complaints or feedback regarding your experience. These inquiries often require personalized attention and access to secure information, ensuring that your specific needs are addressed accurately and efficiently.

Please choose the Type that best fits your query to ensure a swift and accurate response from our team. 
### Type 1 Fillers (General Inquiries and FAQs)
1. "Let's see here..."
   - Use this when transitioning to answer questions about amenities, dining, check-in/out times, etc.

2. "Good question..."
   - Perfect for acknowledging the guest's query before providing information on hotel policies, local attractions, or services.

3. "Just a moment..."
   - Useful when preparing to give detailed responses about the hotel's facilities, special requests, or any general inquiry.

### Type 2 Fillers (Specific Inquiries Requiring External API or Detailed Checks)
1. "Let me check that for you..."
   - Ideal for situations where you need to look up room availability, billing information, or refund status.

2. "I'll need to verify..."
   - Use this before addressing specific concerns that require accessing the guest's personal account or external systems, like invoicing or complaint logging.

3. "Allow me a second to confirm..."
   - Suitable for instances where precise details are needed, and you're about to consult the system or external APIs for accurate information.
   Please provide appropriate filler in a json format {"Type": "<1/2>", "FillerNo": "1/2/3"} "'''

from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Assuming the run_get_category function is defined elsewhere
# def run_get_category(query, system_message):
#     ...

def run_get_category(query, system_message):
    result = get_category(query, system_message)
   # print(f"Query: {query}, Sy= em Message: '{system_message}', Result: {result}")
   # print(datetime.now())
   # print(datetime.now())
    return result

def llama_get_category(query):
    tasks = [
        (query, prompt1),
        (query, prompt2)
    ]
    results = []

    start_time = datetime.now()  # Start timing
    # run_get_category(query, prompt1)
    # print((datetime.now()-start_time).total_seconds())
    # start_time=datetime.now() 
    # run_get_category(query, prompt2)
    # print((datetime.now()-start_time).total_seconds())

    # Using ThreadPoolExecutor to run functions concurrently
    with ThreadPoolExecutor(max_workers=len(tasks)) as executor:
        futures = [executor.submit(run_get_category, task[0], task[1]) for task in tasks]

        for future in as_completed(futures):
            result = future.result()
            results.append(result)

    print((datetime.now() - start_time).total_seconds())

    # print(f"Total time taken: {total_time} seconds")

    return results

def get_subsubcategory(Category, Sub_Category,chat_history, query):
#   def chat_with_user():
    messages = [
        {
            "role": "system",
            "content": (
            '''You are a Hotel receptionist who provides responses to customer queries
            Respond with suitable sub sub category that this user query belongs to.
            FAQ questions include "What is your name?", "Is this the Grand Holiday Hotel?", "Do you have room service?", "Do you have Wi-Fi?", "What's the checkout time?"
            Always respond with following json format {"subsubCategory": "<subsubcategory>"}''' + f'Category: {Category} Sub Category: {Sub_Category}'+ f'User Query: {query}'+ f'Chat History: {messages}'
            ),
        }
    ]

    query = input('user:')
    print(query)
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
            # new_content = content.replace(processed_content, "", 1).strip()  # Remove already processed content
            print(content)

    if content.strip():
        messages.append({"role": "assistant", "content": content.strip()})
        print('final answer:', content.strip())

# chat_with_user()
    
            
        