from playwright.sync_api import sync_playwright
import re
import time
import html
import tkinter as tk
from tkinter.scrolledtext import *
import os, shutil

root=tk.Tk()

# setting the windows size
root.geometry("635x375")
root.title("Wattpad PMs Saver")

# declaring string variable
# for storing name and password
name_var=tk.StringVar()
passw_var=tk.StringVar()
status_var=tk.StringVar()


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

    return cleaned


def submit():

    username=name_var.get()
    password=passw_var.get()
    try:
        users=users_entry_scrolled.get('1.0', 'end')
    
    except:
        pass
    
    status = main(username, password, users)

    if not status:
        status_var.set("There was a critical error with saving the logs.")
    else:
        status_var.set("Logs saved! Find them in the /saved_logs folder.")


def clear_logs():

    if os.path.isdir("saved_logs"):
        shutil.rmtree("saved_logs")
        os.mkdir("saved_logs")
    
    status_var.set("All saved logs were deleted.")



def main(username, password, pmusers):
    
    all_users=pmusers.split()
    # username, password, all users
    status = gather_single_logs(username, password, all_users)

    return status


# creating a label for 
# name using widget Label
name_label = tk.Label(root, text = 'Username', font=('calibre',10, 'bold'))

# creating a entry for input
# name using widget Entry
name_entry = tk.Entry(root,textvariable = name_var, font=('calibre',10,'normal'))

# creating a label for password
passw_label = tk.Label(root, text = 'Password', font = ('calibre',10,'bold'))

# creating a entry for password
passw_entry=tk.Entry(root, textvariable = passw_var, font = ('calibre',10,'normal'), show = '*')

# creating a label for 
# name using widget Label
users_label = tk.Label(root, text = 'Participating PM Users', font=('calibre',10, 'bold'))
space = tk.Label(root, text = ' ', font=('calibre',10, 'bold'))
users_desc1 = tk.Label(root, text = 'Please enter the usernames of those whom you wish to save your PMs with.', font=('calibre',10))
users_desc2 = tk.Label(root, text = 'SEPARATE USERNAMES WITH A SPACE, for example: username1 username2 username3', font=('calibre',10))
users_desc3 = tk.Label(root, text = 'For best results, input all usernames in one go. If you make a mistake, press the delete button and try again.', font=('calibre',10))


users_entry_scrolled = ScrolledText(root, font = ('calibre',10,'normal'), width = 37, height = 5)


# creating a button using the widget 
# Button that will call the submit function 
sub_btn=tk.Button(root,text = 'Submit', command = submit)

clear=tk.Button(root,text = 'Delete Current Saved Logs', command = clear_logs)

final_status = tk.Label(root, textvariable=status_var, font=('calibre',10, 'bold'))

# placing the label and entry in
# the required position using grid
# method
name_label.grid(row=0,column=0)
name_entry.grid(row=1,column=0)
passw_label.grid(row=2,column=0)
passw_entry.grid(row=3,column=0)
space.grid(row=4,column=0)
users_label.grid(row=5,column=0)
users_desc1.grid(row=6,column=0)
users_desc2.grid(row=7,column=0)
users_desc3.grid(row=8,column=0)
users_entry_scrolled.grid(row=9,column=0)
space.grid(row=10,column=0)
sub_btn.grid(row=11,column=0)
clear.grid(row=12,column=0)
space.grid(row=13,column=0)
final_status.grid(row=14,column=0)
# performing an infinite loop 
# for the window to display

root.mainloop()

