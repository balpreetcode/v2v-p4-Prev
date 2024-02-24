


# import sys
# sys.path.append('./components')
# import speech_to_text1
# import part2
# from async_llama2 import llama_get_category


# # query = speech_to_text1.transcribe_stream()
# query = 'I have some issues with payment'
# category_filler = llama_get_category(query)
# print('category_filler:' , category_filler)


# category_filler[['{"Category": "Billing"}'], ['{"Filler": "filler"}']]
# chat_history = []
# info = part2.response_type(query, category_filler, chat_history)

# # print(info)


#################################  Sir

# import sys
# sys.path.append('./components')
# import json
# import speech_to_text1
# from async_llama2 import llama_get_category
# from playFiles import playAudioFile

# # query = speech_to_text1.transcribe_stream()
# query = 'I have some issues with payment'
# answer = llama_get_category(query)
# print('answer:' , answer)
# playAudioFile(answer)

import sys
sys.path.append('./components')
import json
import speech_to_text1
import part2
from async_llama2 import llama_get_category
from playFiles import playAudioFile

# query = speech_to_text1.transcribe_stream()
query = 'I have some issues with payment'

category_filler = llama_get_category(query)
playAudioFile(category_filler)
print('category_filler:' , category_filler)

chat_history = []
info = part2.response_type(query, category_filler, chat_history)
########################################




# if answer == 'prompt_response':
#     print('prompt_response')
# else:
#     print('other_response')

