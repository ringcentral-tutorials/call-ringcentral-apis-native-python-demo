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
    dotenv = Dotenv("./environment/.env-sandbox")
    tokens_file = "tokens_sb.txt"
else:
    dotenv = Dotenv("./environment/.env-production")
    tokens_file = "tokens_pd.txt"
os.environ.update(dotenv)

class RingCentral(object):
    access_token = ""
    def authenticate(self):
        url = os.getenv("RC_SERVER_URL") + "/restapi/oauth/token"
        basic = "%s:%s" % (os.getenv("RC_CLIENT_ID"), os.getenv("RC_CLIENT_SECRET"))
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Accept': 'application/json',
            'Authorization': 'Basic ' + base64.b64encode(basic),
            }
        body = urllib.urlencode({
            'grant_type': 'password',
            'username': os.getenv("RC_USERNAME"),
            'password': os.getenv("RC_PASSWORD")
            })
        if os.path.isfile(tokens_file):
            file = open(tokens_file, 'r')
            tokenObj = json.loads(file.read())
            file.close()
            expire_time = time.time() - tokenObj['timestamp']
            if expire_time < tokenObj['tokens']['expires_in']:
                print ("access_token not expired")
                self.access_token = tokenObj['tokens']['access_token']
                return
            else:
                print ("access_token expired")
                if expire_time < tokenObj['tokens']['refresh_token_expires_in']:
                    print "refresh_token not expired"
                    body = urllib.urlencode({
                        'grant_type': 'refresh_token',
                        'refresh_token': tokenObj['tokens']['refresh_token']
                    })
        # authenticate
        try:
            res = requests.post(url, headers=headers, data=body)
            if res.status_code == 200:
                jsonObj = json.loads(res._content)
                tokensObj = {
                    "tokens": jsonObj,
                    "timestamp": time.time()
                    }
                file = open(tokens_file,'w')
                file.write(json.dumps(tokensObj))
                file.close()
                self.access_token = jsonObj['access_token']
                return
            else:
                raise ValueError(res._content)
        except Exception as e:
            raise ValueError(e)

    # Implement GET request
    def get(self, endpoint, params=None, callback=None):
        try:
            self.authenticate()
            url = os.getenv("RC_SERVER_URL") + endpoint
            if params != None:
                url += "?"
                for key, value in params.items():
    				url += "&%s=%s" % (key, value)

            headers = {
                'Accept': 'application/json',
                'Authorization': 'Bearer ' + self.access_token
                }
            try:
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    if callback is None:
                        return response._content
                    else:
                        callback(response._content)
                else:
                    raise ValueError(response._content)
            except Exception as e:
                raise ValueError(e)
        except Exception as e:
            raise ValueError(e)

    # Implement POST request
    def post(self, endpoint, params=None, callback=None):
        try:
            self.authenticate()
            url = os.getenv("RC_SERVER_URL") + endpoint
            body = None
            if params != None:
                body = json.dumps(params)

            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': 'Bearer ' + self.access_token
                }
            try:
                response = requests.post(url, headers=headers, data=body)
                if response.status_code == 200:
                    if callback is None:
                        return response._content
                    else:
                        callback(response._content)
                else:
                    raise ValueError(response._content)
            except Exception as e:
                raise ValueError(e)
        except Exception as e:
            raise ValueError(e)
