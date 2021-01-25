#import os
import json

#APP_ROOT = os.path.dirname(os.path.abspath(__file__))
def checkLogin(APP_ROOT,email, pin):
    flag = False
    json_file = open(f"{APP_ROOT}/db/user.json", "r")
    users = json.load(json_file)
    json_file.close()
    for user in users:
        if user["email"]==str(email) and user["pin"]==str(pin):
            flag = True
            break
    if flag:
        return flag,user 
    else:
        user1={}
        return flag,user1    