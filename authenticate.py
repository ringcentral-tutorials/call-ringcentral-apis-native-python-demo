import requests
import base64
import urllib
import time
import json
import os
from dotenv import Dotenv
dotenv = Dotenv(".env")
os.environ.update(dotenv)


if os.getenv("ENVIRONMENT") == "sandbox":
    dotenv = Dotenv("../environments/.env-sandbox")
    tokens_file = "tokens_sb.txt"
else:
    dotenv = Dotenv("../environments/.env-production")
    tokens_file = "tokens_pd.txt"
os.environ.update(dotenv)

def get_token():
    url = os.getenv("RC_SERVER_URL") + "/restapi/oauth/token"
    basic = "%s:%s" % (os.getenv("RC_CLIENT_ID"), os.getenv("RC_CLIENT_SECRET"))
    encoded = base64.b64encode(basic)
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Accept': 'application/json',
        'Authorization': 'Basic ' + encoded,
        }
    data = {}
    if os.path.isfile(tokens_file):
        file = open(tokens_file, 'r')
        tokenObj = json.loads(file.read())
        file.close()
        now = time.time() - tokenObj['timestamp']
        print now
        if tokenObj['tokens']['expires_in'] > now:
            print "access_token not expired"
            return tokenObj['tokens']['access_token']
        else:
            print "access_token expired"
            if tokenObj['tokens']['refresh_token_expires_in'] > now:
                print "refresh_token not expired"
                data = {
                    'grant_type': 'refresh_token',
                    'refresh_token': tokenObj['tokens']['refresh_token']
                }
            else:
                print "refresh_token expired"
                data = {
                    'grant_type': 'password',
                    'username': os.getenv("RC_USERNAME"),
                    'password': os.getenv("RC_PASSWORD")
                }
    else:
        data = {
            'grant_type': 'password',
            'username': os.getenv("RC_USERNAME"),
            'password': os.getenv("RC_PASSWORD")
            }

    body = urllib.urlencode(data)
    res = requests.post(url, headers=headers, data=data)
    if res.status_code == 200:
        jsonObj = json.loads(res._content)
        tokensObj = {
            "tokens": jsonObj,
            "timestamp": time.time()
            }
        file = open(tokens_file,'w')
        file.write(json.dumps(tokensObj))
        file.close()
        return jsonObj['access_token']
    else:
        print res._content
        print res.status_code
        return None

def get_account_extensions(access_token):
    endpoint = "/restapi/v1.0/account/~/extension";
    url = os.getenv("RC_SERVER_URL") + endpoint
    headers = {
        'Accept': 'application/json',
        'Authorization': 'Bearer ' + access_token
        }

    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        print res._content
        #return json.loads(res._content)
    else:
        print res.status_code
        return None

access_token = get_token()
if access_token != None:
    res = get_account_extensions(access_token)
    #print res
    if res != None:
        for record in res['records']:
            print "Extension id: %d" % (record['id'])
            if 'extensionNumber' in record:
                print "Extension number: %s" % (record['extensionNumber'])
            if 'name' in record:
                print "Extension name: %s" % (record['name'])
            print "Extension status: %s" % (record['status'])
            if 'type' in record:
                print "Extension type: %s" % (record['type'])
            print "=================="
