
import csv2json
import sys

sys.path.append("./components")

import speech_to_text1
import part1llama
import part2
import streaming_audio


# csv2json.convert_csv_to_json('data.csv')  #converting csv to json

query = speech_to_text1.transcribe_stream()
print(query)

chat_history = []

category = part1llama.get_category(query)
# category = list[str(category)]
info = part2.response_type(query, category)

# print(info)

answer = streaming_audio.final_answer(info, chat_history, query)