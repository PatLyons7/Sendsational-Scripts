import csv
import re


def extract_data(line): 
    name = ''
    phone = ''
    email = ''
    all_time_visits = ''
    last_visit = ''

    # Iterate through each character in the line
    i = 0
    while i < len(line):
        # Extract name until the dash
        if line[i] != '-':
            name += line[i]
            i += 1
        else:
            i += 2  # Skip the dash and the space
            break

    # Extract phone number until the next space or dash
    while i < len(line) and line[i] != ' ' and line[i] != '-':
        phone += line[i]
        i += 1
    i += 1

    if i < len(line) and line[i] == " ":
        i += 1

    # Extract email until the next space or dash
    while i < len(line) and line[i] != ' ' and line[i] != '-':
        email += line[i]
        i += 1
    i += 3
    
    if i < len(line) and line[i] == " ":
        i += 1
        
    # Extract all time visits
    while i < len(line) and line[i].isdigit():
        all_time_visits += line[i]
        i += 1
    i += 1

    # Extract last visit
    while i < len(line):
        if line[i] == "X" or line[i] == '-':
            break
        last_visit += line[i]
        i += 1

    return [name.strip(), phone.strip(), email.strip(), all_time_visits.strip(), last_visit.strip()]


path_to_txt = '/Users/patrick/Desktop/Resy/data.txt'

# Open the text file for reading
with open(path_to_txt, 'r') as file:
    lines = file.readlines()

# Open a CSV file for writing
with open('output.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)

    # Write header
    writer.writerow(['Name', 'Phone', 'Email', 'All time Visits', 'Last Visit'])

    # Extract data from each line and write to CSV
    for line in lines:
        if line.strip():  # Ignore empty lines
            modified_line = re.sub(r'([a-zA-Z])-([a-zA-Z])', r'\1\2', line)
            modified_line = modified_line.replace(' VIP ', ' - ')
            writer.writerow(extract_data(modified_line))

print("Data saved to csv")