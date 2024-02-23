import sys
sys.path.append('./components')
import json
import speech_to_text1
import part2
from async_llama2 import llama_get_category
from async_llama2 import get_subsubcategory
from playFiles import playAudioFile

# query = speech_to_text1.transcribe_stream()
query = 'I have some issues with payment'
print('temp')
category_filler = llama_get_category(query)
type_value, filler_no,Category,Sub_Category=playAudioFile(category_filler)
print('category_filler:' , category_filler)
print('type_value:', type_value)
print('filler_no:', filler_no)
print('Category:', Category)
print('Sub_Category:', Sub_Category)
# get_subsubcategory(Category, Sub_Category, query)
chat_history = []
info = part2.response_type(query, category_filler, chat_history)