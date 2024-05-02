import json
from numpy import random
import numpy as np
import requests
import time
import itertools
from playwright.sync_api import sync_playwright


# username of both parties in a chat 
# will be input into a text file by the program user
# and processed from there. 
def gather_single_logs(party1, party2):
    try:
        
        link = 'https://www.wattpad.com/api/v3/users/' + party1 + '/inbox/' + party2 + '?offset=0&limit=100'

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
                   'referer': 'https://www.wattpad.com/inbox/ThunderingLight'
                  }
        result = requests.get(link, headers=headers)
        # print(result.content.decode())
        #parse it (basically)
        jsonResponse = result.json()
        print(result)

        file_name = 'logs_with' + party2 + '.txt'

        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(jsonResponse, f, ensure_ascii=False, indent=4)
    except:
        print("failed")
    
def main():

    payload = {
    'inUserName': 'rosienekochan',
    'inUserPass': 'test'
    }
    
    with requests.Session() as s:
        p = s.post('https://wattpad.com/login', data=payload)

        print(p.text)

        
        parties = open("usernames.txt", "r")
        all_users = parties.read().splitlines()
        username = all_users.pop(0)
        
        for party in all_users:
            gather_single_logs(username, party)

        print("finished")

main()

