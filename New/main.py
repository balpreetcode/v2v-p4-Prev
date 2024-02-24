import sys
sys.path.append('./components')
import json
import speech_to_text1
import part2
from async_llama2 import llama_get_category, get_subsubcategory
from playFiles import playAudioFile
import csv2json

# csv2json.convert_csv_to_json('data.csv')

while True:
    # query = speech_to_text1.transcribe_stream()
    # query = 'I have some issues with payment'
    query = 'What is the checkout time'
    # print('temp')
    category_filler = llama_get_category(query)
    type_value, filler_no,Category,Sub_Category=playAudioFile(category_filler)
    print('category_filler:' , category_filler)
    print('type_value:', type_value)
    print('filler_no:', filler_no)
    print('Category:', Category)
    print('Sub_Category:', Sub_Category)

    chat_history = []
    # get_subsubcategory(Category, Sub_Category, chat_history, query)

    # category = json.loads(Category, Sub_Category)
    category = {
        'Category': Category,
        'Sub Category': Sub_Category
    }

    # if type_value == '1':
    #     print('Yes')
    # else:
    #     print('No')
    info = part2.response_type(query, category, type_value, chat_history)