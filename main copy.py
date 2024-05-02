from playwright.sync_api import sync_playwright
import re
import time
import html

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

            flag = True
            offset = 0
            while flag:
                content = page.content()
                make_files(content, party2)

                if "nextUrl" not in content:
                    flag = False

                else:
                    # idxStart = [idxStart.end() for idxStart in re.finditer('"nextUrl":"', content)]
                    # idxEnd = [idxEnd.start() for idxEnd in re.finditer('"}', content)]

                    # nextUrl = content[idxStart[0]:idxEnd[0]]
                    # page.goto(nextUrl)

                    offset += 100
                    nextUrl = 'https://www.wattpad.com/api/v3/users/' + party1 + '/inbox/' + party2 + '?offset=' + str(offset) +'&limit=100'
                    time.sleep(0.02)
                    page.goto(nextUrl)

            return True

    except Exception as error:
        print(error)


def make_files(content, name):
        dump = open('html_dump.txt', 'w')
        dump.write(content)
        dump.close()
        
        cleaned = clean_logs(content)

        file_name = 'logs_with_' + name + '.txt'
        file = open(file_name, 'a')
        file.write('\n'.join(str(line) for line in cleaned))
        file.close()


def clean_logs(content):

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

        message = html.unescape(content[idxBodyEnd[i]+1:idxDateStart[i]-1])
        message = message.replace('\\n', ' ').replace('\\"', '"').replace('\'', "'")

        date = content[idxDateEnd[i]+1:idxUserStart[i]-1]
        user = content[idxNameEnd[i]+1:idxRealNameStart[i]-1]

        pm['from'] = user
        pm['date'] = date
        pm['message'] = message

        cleaned.append(pm)
    
    reversed_clean = list(reversed(cleaned))

    return cleaned


def main():

    parties = open("usernames.txt", "r")
    all_users = parties.read().splitlines()
    username = all_users.pop(0)
    
    for party in all_users:
        status = gather_single_logs(username, party)

    if status:
        print('Logs saved!')
    else:
        print('Error - could not save logs.')
    

main()

