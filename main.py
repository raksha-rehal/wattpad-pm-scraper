from playwright.sync_api import sync_playwright
import re
import time
import html

# https://www.youtube.com/watch?v=H2-5ecFwHHQ

# username of both parties in a chat 
# will be input into a text file by the program user
# and processed from there. 
def gather_single_logs(username, password, all_users):
    try:
        
        with sync_playwright() as p:

            login = "https://wattpad.com/login"

            browser = p.chromium.launch(headless=False)
            page = browser.new_page()

            page.goto(login)
            page.locator('"Log in"').click()
            page.fill('input#login-username', username)
            page.fill('input#login-password', password)
            page.locator('"Log in"').click()

            for party2 in all_users:
                url = 'https://www.wattpad.com/api/v3/users/' + username + '/inbox/' + party2 + '?offset=0&limit=100'

                page.goto(url)

                flag = True
                offset = 0
                while flag:
                    content = page.content()
                    make_files(content, party2)

                    if "nextUrl" not in content:
                        flag = False

                    else:
                        offset += 100
                        nextUrl = 'https://www.wattpad.com/api/v3/users/' + username + '/inbox/' + party2 + '?offset=' + str(offset) +'&limit=100'
                        time.sleep(0.02)
                        page.goto(nextUrl)
            
            page.wait_for_timeout(1000)

        for party2 in all_users:

            file_name = 'saved_logs/logs_with_' + party2 + '.txt'

            # read lines in an array called lines
            f1 = open(file_name, "r")
            line_list = f1.readlines()
            line_list.reverse()
            f1.close()

            f2 = open(file_name, 'w')
            f2.write('\n'.join(str(line) for line in line_list))
            f2.close()

        return True

    except Exception as error:
        print(error)


def make_files(content, name):        
        cleaned = clean_logs(content)

        file_name = 'saved_logs/logs_with_' + name + '.txt'
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

    auth = open("authentication.txt", "r")
    userPass = auth.read().splitlines()
    
    # username, password, all users
    status = gather_single_logs(userPass[0], userPass[1], all_users)

    if status:
        print('Logs saved!')
    else:
        print('Error - could not save logs.')
    

main()

