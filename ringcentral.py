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
            if tokenObj['tokens']['expires_in'] > now:
                print "access_token not expired"
                self.access_token = tokenObj['tokens']['access_token']
                return
                #return tokenObj['tokens']['access_token']
            else:
                print "access_token expired"
                if tokenObj['tokens']['refresh_token_expires_in'] > now:
                    print "refresh_token not expired"
                    data = {
                        'grant_type': 'refresh_token',
                        'refresh_token': tokenObj['tokens']['refresh_token']
                    }
                # else:
                #     print "refresh_token expired"
                #     data = {
                #         'grant_type': 'password',
                #         'username': os.getenv("RC_USERNAME"),
                #         'password': os.getenv("RC_PASSWORD")
                #     }
        # else:
        #     data = {
        #         'grant_type': 'password',
        #         'username': os.getenv("RC_USERNAME"),
        #         'password': os.getenv("RC_PASSWORD")
        #         }
        data = {
            'grant_type': 'password',
            'username': os.getenv("RC_USERNAME"),
            'password': os.getenv("RC_PASSWORD")
            }
        body = urllib.urlencode(data)
        try:
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
                self.access_token = jsonObj['access_token']
                return
                #return jsonObj['access_token']
            else:
                raise ValueError(res._content)
        except Exception as e:
            raise ValueError(e)

    def get(self, endpoint, params=None, callback=None):
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
            res = requests.get(url, headers=headers)
            if res.status_code == 200:
                if callback is None:
                    return res
                else:
                    callback(res)
            else:
                raise ValueError(res._content)
        except Exception as e:
            raise ValueError(e)

    def post(self, endpoint, params=None, callback=None):
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
            res = requests.post(url, headers=headers, data=body)
            if res.status_code == 200:
                if callback is None:
                    return res
                else:
                    callback(res)
            else:
                raise ValueError(res._content)
        except Exception as e:
            raise ValueError(e)
