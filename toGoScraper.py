import requests
import json
import csv
import os

def file_exists(file_path):
    return os.path.isfile(file_path)

url = "https://api.togoorder.com/api/MerchantReport/OrderReportRest/"

id = 3000

while id < 5000:
    payload = json.dumps({
    "merchantId": id,
    "start": "20150101000000",
    "end": "20250802235959",
    "dateColumn": "TimeOfOrder",
    "pageNumber": "1",
    "pageSize": "100000",
    "orderBy": "",
    "direction": "asc",
    "filters": {}
    })
    headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json',
    'Origin': 'https://togotechnologies.com',
    'Referer': 'https://togotechnologies.com/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'cross-site',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    if response.text == "[]":
        print("skipped", id)
    else:
        orders = response.json()

        headers = list(orders[0].keys())

        columns = {header: [] for header in headers}

        for order in orders:
            for header in headers:
                columns[header].append(order.get(header, ""))

        csv_file_path = 'orders.csv'
        writeHeader = True
        if file_exists(csv_file_path):
            writeHeader = False


        with open(csv_file_path, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)

            # Check if the file exists
            if writeHeader:
                writer.writeheader()

            # Write or append data
            for i in range(len(orders)):
                writer.writerow({header: columns[header][i] for header in headers})

        print(id, "added to csv")
    id += 1
