import csv
import json

def convert_csv_to_json(csv_file_path):

    # Initialize a list to hold the structured data
    structured_data = []

    # Read CSV data
    with open(csv_file_path, mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            structured_data.append(row)

    # Convert the structured data to JSON
    json_data = json.dumps(structured_data, indent=4)

    # Output the JSON data
    print(json_data)

    # If you want to save the JSON data to a file, uncomment the following lines:
    with open('data.json', 'w', encoding='utf-8') as json_file:
        json_file.write(json_data)

# # Assuming CSV data is stored in 'data.csv'
# csv_file_path = 'data.csv'

# # Initialize a list to hold the structured data
# structured_data = []

# # Read CSV data
# with open(csv_file_path, mode='r', encoding='utf-8') as csv_file:
#     csv_reader = csv.DictReader(csv_file)
#     for row in csv_reader:
#         structured_data.append(row)

# # Convert the structured data to JSON
# json_data = json.dumps(structured_data, indent=4)

# # Output the JSON data
# print(json_data)

# # If you want to save the JSON data to a file, uncomment the following lines:
# with open('data.json', 'w', encoding='utf-8') as json_file:
#     json_file.write(json_data)