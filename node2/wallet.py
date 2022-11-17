import os
import json
from hashlib import md5

def new_account():
    try:
        # if account exists
        # load account
        with open("myaccount.json",'r') as file:
            content = json.load(file)
            pub_key = content["public_key"]
            print("**Error: Account exists. Cannot create again!**")
    except FileNotFoundError:
        private_key = os.urandom(32)
        public_key = md5(private_key).hexdigest()
        content = {
            "public_key": public_key,
        }
        with open("myaccount.json",'w') as file:
            json.dump(content, file)
        with open("myaccount.json",'r') as file:
            content = json.load(file)
            pub_key = content["public_key"]
            print("**Account created**")      
    print('public_key: ', pub_key)
    return pub_key

def read_account():
    try:
        with open("myaccount.json",'r') as file:
            content = json.load(file)
            pub_key = content["public_key"]
            return pub_key
    except FileNotFoundError:
        print("**Error: Please create your account before voting!**")
    


def account_exist():
    try:
        with open("myaccount.json",'r') as file:
            content = json.load(file)
            if len(content) == 0:
                return False
            else:
                return True
    except FileNotFoundError:
        return False

if __name__ == '__main__':
    new_account()