import requests
from playwright_stealth import stealth_sync
from playwright.sync_api import sync_playwright
import json

email = '' # FILL IN
password = '' # FILL IN

#LOGIN AND INTERCEPT TOKEN
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=1000)
    page = browser.new_page()
    page.goto("https://oauth.rebrandly.com/Account/Login?ReturnUrl=%2Fconnect%2Fauthorize%2Fcallback%3Fclient_id%3D1FEB3DDD-8AC7-4F83-A2B3-ED4EB558DFA2%26redirect_uri%3Dhttps%253A%252F%252Fapp.rebrandly.com%26state%3DeyJwYXRoIjoiL2xpbmtzIn0%253D%26response_type%3Dcode%26acr_values%3Dcmd%253Arelogin%2520flow%253Auser%2520plan%253A16f08fb9749d417eb142a326a2d0527c%26scope%3Drbapi%2520offline_access%2520rbapikeys%2520rbinvites%2520rbdowngrade")
    page.fill('input#Email.float-left', email )
    page.fill('input#Password', password )
    page.keyboard.press("Enter")
    page.wait_for_timeout(7500)
    token = page.evaluate('''() => {return localStorage.getItem("token");}''')
    token_dict = json.loads(token)
    token = token_dict['access_token']
    

payload = {}
headers = {'Authorization': f'Bearer {token}'}
stats = ['platforms', 'devices', 'browsers', 'weekdays', 'dayhours'] #All Stats you want for each account
linkIds = ['45d7547d991d4cf194fbeb8ad827d6a7'] #All the link IDs for each unique link

#GET STATS FOR EACH UNIQUE LINK
for linkId in linkIds:
    for stat in stats:
        url = f"https://api.rebrandly.com/v1/links/{linkId}/segments?group={stat}"

        response = requests.request("GET", url, headers=headers, data=payload)

        print(f"{stat}: {linkId} ", "\n", response.text, "\n")

