import json
from numpy import random
import numpy as np
import requests
import time
import itertools
from playwright.sync_api import sync_playwright

# https://www.youtube.com/watch?v=H2-5ecFwHHQ

# username of both parties in a chat 
# will be input into a text file by the program user
# and processed from there. 
def gather_single_logs(party1, party2):
    try:
        with sync_playwright() as p:

            url = 'https://www.wattpad.com/api/v3/users/' + party1 + '/inbox/' + party2 + '?offset=0&limit=100'

            ua = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64)" 
                  "AppleWebKit/537.36 (KHTML, like Gecko)" 
                  "Chrome/124.0.0.0 Safari/537.36"
                )
            
            login = "https://wattpad.com/login"

            browser = p.chromium.launch(headless=False)
            page = browser.new_page(user_agent=ua)
            page.goto(login)
            #page.click('button[class=btn-block btn-primary]')
            page.locator('"Log in"').click()

            page.fill('input#login-username', 'rosienekochan')
            page.fill('input#login-password', 'test')

            page.locator('"Log in"').click()
            
            page.goto(url)

            page.wait_for_timeout(100000)
            
            html = page.content()
            
        print(html)
        
        # result = requests.get(url, headers=headers)
        # # print(result.content.decode())
        # #parse it (basically)
        # jsonResponse = result.json()
        # print(result)

        # file_name = 'logs_with' + party2

        # with open(file_name, 'w', encoding='utf-8') as f:
        #     json.dump(jsonResponse, f, ensure_ascii=False, indent=4)

    except Exception as error:
        print(error)
    
def main():

    parties = open("usernames.txt", "r")
    all_users = parties.read().splitlines()
    username = all_users.pop(0)
    
    for party in all_users:
        gather_single_logs(username, party)

    print("finished")
    

main()

