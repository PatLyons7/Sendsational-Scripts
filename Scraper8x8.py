import requests
import json
import csv

def getAccessToken(apiKey, username, password):
    url = "https://api.8x8.com/analytics/work/v1/oauth/token"

    payload = f'username={username}&password={password}'
    headers = {
    '8x8-apikey': apiKey,
    'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    response_dict = json.loads(response.text)
    access_token = "Bearer " + response_dict["access_token"]
    print(access_token)
    return access_token

def getRecords(startTime, endTime, pageSize, accessToken, apiKey, csvFileName):

    url = f"https://api.8x8.com/analytics/work/v2/call-records?pbxId=allpbxes&startTime={startTime}&endTime={endTime}&timeZone=America/New_York&pageSize={pageSize}"
    
    payload = {}
    headers = {
     'Authorization': accessToken,
        '8x8-apikey': apiKey
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    response_dict = json.loads(response.text)

    # Access the scrollId and totalRecordCount from the dictionary
    meta_data = response_dict.get("meta", {})
    scroll_id = meta_data.get("scrollId")
    total_record_count = meta_data.get("totalRecordCount")

    # Extract desired fields and write to CSV
    fields_to_extract = ["startTime", "caller", "callerName", "callerId"]

    with open(csvFileName, mode='w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fields_to_extract)
        writer.writeheader()

        for call_record in response_dict["data"]:
            row = {field: call_record.get(field, "") for field in fields_to_extract}
            writer.writerow(row)
            total_record_count -= 1
            print(total_record_count)

    print(f"CSV file '{csvFileName}' has been created with the extracted fields.")
    print("TOTAL LEFT", total_record_count)
    return scroll_id, total_record_count


def getFollowingRecords(startTime, endTime, pageSize, scrollId, accessToken, apiKey, totalRecordCount, csvFileName):

    url = f"https://api.8x8.com/analytics/work/v2/call-records?pbxId=allpbxes&startTime={startTime}&endTime={endTime}&timeZone=America/New_York&pageSize={pageSize}&scrollId={scrollId}"
    
    payload = {}
    headers = {
     'Authorization': accessToken,
        '8x8-apikey': apiKey
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    response_dict = json.loads(response.text)

    # Access the scrollId and totalRecordCount from the dictionary
    meta_data = response_dict.get("meta", {})
    scroll_id = meta_data.get("scrollId")

    # Extract desired fields and write to CSV
    fields_to_extract = ["startTime", "caller", "callerName", "callerId"]

    with open(csvFileName, mode='a', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fields_to_extract)

        for call_record in response_dict["data"]:
            row = {field: call_record.get(field, "") for field in fields_to_extract}
            writer.writerow(row)
            totalRecordCount -= 1
            print(totalRecordCount)

    print(f"CSV file '{csvFileName}' has been appeneded to.")
    print("TOTAL LEFT", totalRecordCount)
    return scroll_id, totalRecordCount



# MAIN ------------------------------> 
# Credentials
apiKey = "" # FILL IN
username = "" # FILL IN
password = "" # FILL IN
accessToken = getAccessToken(apiKey, username, password)

# Parameters
startTime = "2023-07-01 00:00:00"
endTime = "2023-07-08 22:15:00"
pageSize = "50"

# CSV File
csvFileName = "8x8_call_records.csv"

# Get original data
scrollId, totalRecordCount = getRecords(startTime, endTime, pageSize, accessToken, apiKey, csvFileName)

# Get any following pages
while totalRecordCount > 0:
    scrollId, totalRecordCount = getFollowingRecords(startTime, endTime, pageSize, scrollId, accessToken, apiKey, totalRecordCount, csvFileName)


# This function is only for the Sottosopra account to clean its CSV file ----------------------------------------->
def sopraCSVCleaner(inputFile, outputFile):
    # Open input and output CSV files
    with open(inputFile, mode='r') as csv_in_file, open(outputFile, mode='w', newline='') as csv_out_file:
        reader = csv.DictReader(csv_in_file)
        fieldnames = reader.fieldnames
        
        # Write header to the output file
        writer = csv.DictWriter(csv_out_file, fieldnames=fieldnames)
        writer.writeheader()
        
        # Process rows
        for row in reader:
            # Check if callerName is not "sotto sopra" and keep only first 10 characters of startTime
            if row['callerName'] != 'sotto sopra':
                row['startTime'] = row['startTime'][:10]
                writer.writerow(row)

# Output filename
output_filename = 'SottoSopra.csv' 

# Process the CSV file
sopraCSVCleaner(csvFileName, output_filename)

print(f"CSV file '{csvFileName}' processed. Rows with 'callerName' as 'sotto sopra' removed and 'startTime' trimmed to 10 characters in '{output_filename}'.")