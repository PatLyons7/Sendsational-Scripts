import pytesseract 
from pdf2image import convert_from_path
import re
import csv
import os
from datetime import datetime
import pandas as pd

# Directory containing your PDF files
directory_path = '/Users/patrick/Desktop/OCR Yummy/Test PDF'

terminating_phone = r"tenmineting|temineting|temineting|terminafing|temvineting|temminating|temrinating|tenrinating|tenrineting|tenrinating|tervineting|terineting|tenrinating|temminating|fenrinating|temrinating|termvinating|tenrinating|fermineting|fervinating|tenvinefing|fenvineting|ferrinating|femvinating|ferminating|fenvineting|teninating|ferminating|temvinating|fenvinating|ferminating|tenvinating|ferrinating|tervinating|terrinating|femrinating|fenvineting|terrinating|ferrineting|ferineting|ferinating|ferminating|ferrineting|tenvinating|ferineting|tenvinating|terninating|femineting|terrinating|terinating|tenvinating|teminating|terrineting|terinating|terminating|terrineting|femminating|tenvinating|ferinating|teminating|tenvineting|terinating|tervinating|tervinating|terminating|ferinating|teminating|termineting|teminating|tenvinaling|feminating|tervinating|feminating|tervinating|ferrinating|tenvineting|tenminating|termineting|feminating|tervinating|terminating|teminating"

def cleanText(text):
    text = insert_termphone(text, terminating_phone, "TERMPHONE")
    text = remove_lines_under_terphone(text)
    text = remove_below_date(text)
    text = remove_first_line(text)
    text = process_text(text)
    return text

def insert_termphone(text, pattern, replacement):
    lines = text.split('\n')
    regex = re.compile(pattern, re.IGNORECASE)
    for i, line in enumerate(lines):
        if regex.search(line):
            lines[i] = replacement
    return '\n'.join(lines)


def remove_lines_under_terphone(text):
    lines = text.split('\n')  # Split the text into lines
    start_index = None  # Initialize start index to None
    end_index = None  # Initialize end index to None

    # Find the first index of TERMPHONE and the index where space is encountered after TERMPHONE
    for i, line in enumerate(lines):
        if re.match(r'\bTERMPHONE\b', line.strip()):
            start_index = i-1
        elif start_index is not None and line.strip() == '':
            end_index = i
            break  # Stop searching once space is encountered after TERMPHONE

    # If both start_index and end_index are found, return the text without lines from start_index+1 to end_index
    if start_index is not None and end_index is not None:
        del lines[start_index+1:end_index]
    
    # Join the modified lines back into a single string
    modified_text = '\n'.join(lines)
    return modified_text

def remove_below_date(text):
    lines = text.split('\n')  # Split the text into lines
    last_date_line_index = -1  # Initialize index to store the last line with date format

    # Find the index of the last line with the date format
    for i, line in enumerate(lines):
        if line.strip() and re.match(r'\d{4}-\d{2}-\d{2}', line.strip()):
            last_date_line_index = i

    # Return the text block from the line with the last date
    if last_date_line_index != -1:
        return '\n'.join(lines[:last_date_line_index + 1])

    # If no date line is found, return the original text
    return text[1:]

def remove_first_line(text):
    lines = text.split('\n')  # Split the text into lines
    #if len(lines) > 1:
        # lines.pop(1)  # Remove the first line if there is more than one line
    
    # Join the remaining lines back into a single string
    modified_text = '\n'.join(lines[1:])
    return modified_text

def big_block_extractor(text):
    lines = text.split('\n')

    phone_numbers = []
    datetime1 = []
    datetime2 = []

    for line in lines:
        items = line.split()
        if len(items) >= 2:
            phone_numbers.append(items[0])
            datetime1.append(items[2].split()[0])
            datetime2.append(items[4].split()[0])

    return phone_numbers, datetime1, datetime2

def format_output(phone_numbers, datetime1, datetime2):
    output = []
    output.append('\n'.join(phone_numbers))
    output.append('\n\nDATETIME1')
    output.append('\n'.join(datetime1))
    output.append('\n\nDATETIME2')
    output.append('\n'.join(datetime2))
    return '\n'.join(output)


def process_text(text):
    lines = text.split('\n')
    big_block_found = False  # Initialize big block flag

    for line in lines:
        if line.strip():  # Check if line is non-blank
            if len(line) > 15:
                big_block_found = True
                break  # Exit loop if big block found
            else: 
                break

    if big_block_found:
        return process_big_block(text)
    else:
        return process_normal_block(text)

def process_big_block(text):
    phone_numbers, datetime1, datetime2 = big_block_extractor(text)
    formatted_output = format_output(phone_numbers, datetime1, datetime2)
    return formatted_output

def process_normal_block(text):
    lines = text.split('\n')
    count = 1
    for i in range(len(lines)):
        if "_" in lines[i]:
            lines[i] = f"DATETIME{count}"
            count += 1
    return '\n'.join(lines)


def replace_parentheses_with_zeros(input_string):
    return input_string.replace("(", "0").replace(")", "0") if ")" in input_string or "(" in input_string else input_string



def get_most_recent_date(date_strings):
    valid_dates = []
    for date_str in date_strings:
        if date_str is not None:
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                valid_dates.append(date_obj)
            except ValueError:
                pass

    if valid_dates:
        most_recent_date = max(valid_dates)
        return most_recent_date.strftime("%Y-%m-%d")
    else:
        # most_recent_date = datetime.strptime("1999-01-01", "%Y-%m-%d")
        return datetime.strptime("1999-01-01", "%Y-%m-%d")


def text_to_dictionary(text):
    lines = text.split('\n')

    phone_numbers = []
    datetimes1 = []
    datetimes2 = []
    dt1 = False
    dt2 = False

    for line in lines:
        if "DATETIME1" in line:
            dt1 = True
            continue
        elif "DATETIME2" in line:
            dt2 = True
            continue

        datetime_str = line[:10]
        cleanedDatetime = replace_parentheses_with_zeros(datetime_str)
        
        if dt1 and not dt2:
            datetimes1.append(cleanedDatetime)
        elif dt1 and dt2:
            datetimes2.append(cleanedDatetime)

        else:
            cleanedNum = ''.join(char for char in line if char.isdigit())
            phone_numbers.append(cleanedNum)

    # Create dictionary with phone numbers as keys and a tuple of datetimes1 and datetimes2 as values
    result_dict = {}
    for i, phone_number in enumerate(phone_numbers):
        if i < len(datetimes1):
            datetime1 = datetimes1[i]
        else:
            datetime1 = None

        datetime2 = None
        if i < len(datetimes2):
            datetime2 = datetimes2[i]

        result_dict[phone_number] = (datetime1, datetime2)

    filtered_dict = {}
    for key, value in result_dict.items():
        if key.isdigit() and len(key) == 10:
            filtered_dict[key] = get_most_recent_date(value)


    return filtered_dict
    
def write_to_csv(data_dict, file_name):
    file_exists = os.path.isfile(file_name)

    with open(file_name, mode='a' if file_exists else 'w', newline='') as file:
        fieldnames = ['Phone Numbers', 'Recent Date']
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        for phone_number, recent_date in data_dict.items():
            writer.writerow({'Phone Numbers': phone_number, 'Recent Date': recent_date})


# Open test.txt in append mode
with open('test.txt', 'a') as file:
    # Loop through all files in the directory
    for i, filename in enumerate(os.listdir(directory_path)):
        print(filename)
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(directory_path, filename)
            images = convert_from_path(pdf_path)

            for idx, image in enumerate(images):
                print("image "+ str(idx+1))
                #file.write('START PAGE ' + str(idx+1) + "\n")
                text = pytesseract.image_to_string(image)
                cleanedText = cleanText(text)
                #file.write(cleanedText + '\nEND PAGE ' + str(idx+1) + "\n")
                dictionary = text_to_dictionary(cleanedText)
                write_to_csv(dictionary, 'YummyCSV.csv')
                

# CSV CLEANER ------------------------>
# Read the CSV file into a DataFrame
df = pd.read_csv('YummyCSV.csv')

# Convert the 'Date' column to datetime format, handling extra characters
df['Recent Date'] = pd.to_datetime(df['Recent Date'].str.strip(), errors='coerce')

# Replace NaT (Not a Time) values with '1999-01-01'
df['Recent Date'].fillna(pd.Timestamp('1999-01-01'), inplace=True)

# Format the date column to YYYY-MM-DD
df['Recent Date'] = df['Recent Date'].dt.strftime('%Y-%m-%d')

# Group by 'Phone Numbers' and keep the latest date for each phone number
df = df.sort_values('Recent Date').groupby('Phone Numbers', as_index=False).last()

# Write the updated DataFrame to a new CSV file
df.to_csv('updated_csv_file.csv', index=False)



