from ringcentral import *
import os

rc = RingCentral()

# Use call back
def callback(response):
    print response._content

def get_account_extension():
    try:
        endpoint = "/restapi/v1.0/account/~/extension";
        params = {'status':'Enabled'}
        rc.get(endpoint, params, callback)
    except Exception as e:
        print (e)

def send_sms(toNumber, message):
    try:
        endpoint = "/restapi/v1.0/account/~/extension/~/sms";
        params = {'from' : {'phoneNumber' : os.getenv("RC_USERNAME")},
                   'to' : [{'phoneNumber' : toNumber}],
                   'text' : message
                 };
        rc.post(endpoint, params, callback)
    except Exception as e:
        print (e)


get_account_extension()
send_sms('+1XXXXXXXXXX', 'Hello World!')
