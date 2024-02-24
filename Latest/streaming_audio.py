
import openai
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Access environment variables
PPLX_API_KEY = os.environ.get("PPLX_API_KEY")
os.environ["PPLX_API_KEY"] = PPLX_API_KEY

model_name="llama-2-70b-chat"

def final_answer(info, chat_history, query):
    messages = [
        {
            "role": "system",
            "content": (
                '''You are a receptionist of a hotel, answer the user's query based on the provided info. You will also be provided with chat history
                '''+ str(chat_history) + f'Info: {info}'
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