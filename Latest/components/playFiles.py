import json
import sounddevice as sd
import soundfile as sf


filename = 'letmecheck.wav'

def getjson(text):
     print('text')
     type_value = ''
     filler_no = ''
     Category = ''
     Sub_Category = ''
     for item in text:
        # Remove newline characters and load the JSON string into a Python dictionary
        category_dict = json.loads(item[0].replace('\n', ''))
        
        # Check if the dictionary has 'Category' or 'FillerNo' and update the variables accordingly
        if 'Type' in category_dict:
            type_value = category_dict['Type']
        if 'Category' in category_dict:
            Category = category_dict['Category']
        if 'Sub Category' in category_dict:
            Sub_Category = category_dict['Sub Category']
        if 'FillerNo' in category_dict:
            filler_no = category_dict['FillerNo']
           
     return type_value, filler_no,Category,Sub_Category

# Replace 'your_file_path' with the path to your audio file
def playAudioFile(answer):
    # Iterate over each JSON string in the 'answer' list
    type_value, filler_no,Category,Sub_Category = getjson(answer)
    file_name = f'assets/fillers/cat{type_value}fillerno{filler_no}.wav'
    print(file_name)
    play_audio(file_name)
    # play the audio file filename
    return type_value, filler_no,Category,Sub_Category

def play_audio(filename):
    d, fs = sf.read(filename)
    sd.play(d, fs)
    # sd.wait()
    