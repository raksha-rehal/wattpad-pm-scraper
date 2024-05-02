import json
from playwright.sync_api import sync_playwright
import re

# https://www.youtube.com/watch?v=H2-5ecFwHHQ

# username of both parties in a chat 
# will be input into a text file by the program user
# and processed from there. 
def gather_single_logs(party1, party2):
    try:
        with sync_playwright() as p:

            url = 'https://www.wattpad.com/api/v3/users/' + party1 + '/inbox/' + party2 + '?offset=0&limit=100'
            login = "https://wattpad.com/login"

            ua = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64)" 
                  "AppleWebKit/537.36 (KHTML, like Gecko)" 
                  "Chrome/124.0.0.0 Safari/537.36"
                )

            browser = p.chromium.launch(headless=False)
            page = browser.new_page(user_agent=ua)

            page.goto(login)
            page.locator('"Log in"').click()
            page.fill('input#login-username', 'rosienekochan')
            page.fill('input#login-password', 'test')
            page.locator('"Log in"').click()    
            page.goto(url)

            page.wait_for_timeout(1000)
            
            content = page.content()
        
        cleaned = clean_logs(content, party2)

        file_name = 'logs_with_' + party2 + '.txt'

        file = open(file_name, 'w')
        #file.write(str(cleaned))
        file.write('\n'.join(str(line) for line in cleaned))

        file.close()

    except Exception as error:
        print(error)
    

def clean_logs(content, name):

    #"body":
    #,"createDate":
    #,"from":
    # "name":
    # ,"realname":

    cleaned = []
    
    # bodyEnd - dateStart is the whole message
    # dateEnd - userStart is the date sent
    # nameEnd - realNameStart is the user who sent the message

    idxBodyEnd = [idxBodyEnd.end() for idxBodyEnd in re.finditer('"body":', content)]
    idxDateStart = [idxDateStart.start() for idxDateStart in re.finditer(',"createDate":', content)]
    
    idxDateEnd = [idxDateEnd.end() for idxDateEnd in re.finditer(',"createDate":', content)]
    idxUserStart = [idxUserStart.start() for idxUserStart in re.finditer(',"from":', content)]
    
    idxNameEnd = [idxNameEnd.end() for idxNameEnd in re.finditer('"name":', content)]
    idxRealNameStart = [idxRealNameStart.start() for idxRealNameStart in re.finditer(',"realname":', content)]

    #print(len(idxBodyEnd), len(idxDateStart), len(idxDateEnd), len(idxUserStart), len(idxNameEnd), len(idxRealNameStart))
    
    for i in range(len(idxBodyEnd)):
        pm = {}

        message = content[idxBodyEnd[i]:idxDateStart[i]]
        date = content[idxDateEnd[i]:idxUserStart[i]]
        user = content[idxNameEnd[i]:idxRealNameStart[i]]

        pm['from'] = user
        pm['date'] = date
        pm['message'] = message

        cleaned.append(pm)

    return list(reversed(cleaned))


def main():

    parties = open("usernames.txt", "r")
    all_users = parties.read().splitlines()
    username = all_users.pop(0)
    
    for party in all_users:
        gather_single_logs(username, party)

    print("finished")
    

main()

