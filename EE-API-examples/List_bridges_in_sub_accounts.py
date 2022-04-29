import requests
import json
import sys
import local_settings

###
# Setup Information
###


# automatically manage cookies between requests
session = requests.Session()

# Enter your credentials
username = ""
password = ""
api_key = ""

if username == "" or password == "" or api_key == "":
    
    # look to see if there are credentials in local_settings.py
    username = local_settings.username
    password = local_settings.password
    api_key = local_settings.api_key

    if username == "" or password == "" or api_key == "":
        print("Please put in your credentials")
        sys.exit()




# Translating the HTTP response codes to make the status messages easier to read
HTTP_STATUS_CODE = { 
    200: 'OK', 
    202: 'ACCEPTED',
    400: 'Bad Request, please check what you are sending',
    401: 'User needs to Login first', 
    403: 'User does not have access to that',
    500: 'API had a problem (500)',
    502: 'API had a problem (502)',
    503: 'API had a problem (503)'
    }




###
# Step 1: login (part 1)
# make sure put in valid credentials
###

url = "https://login.eagleeyenetworks.com/g/aaa/authenticate"

payload = json.dumps({'username': username, 'password': password})
headers = {'content-type': 'application/json', 'authorization': api_key }

response = session.request("POST", url, data=payload, headers=headers)

print ("Step 1: %s" % HTTP_STATUS_CODE[response.status_code])
token = response.json()['token']



###
# Step 2: login (part 2)
###

url = "https://login.eagleeyenetworks.com/g/aaa/authorize"

querystring = {"token": token}

payload = json.dumps({ 'token': token })
headers = {'content-type': 'application/json', 'authorization': api_key }

response = session.request("POST", url, data=payload, headers=headers)

print("Step 2: %s" % HTTP_STATUS_CODE[response.status_code])

current_user = response.json()


###
# Step 3: get list a sub-accounts
###

url = f"https://{current_user['active_brand_subdomain']}.eagleeyenetworks.com/g/account/list"

payload = ""
headers = {'authorization': api_key }
response = session.request("GET", url, data=payload, headers=headers)

print("Step 3: %s" % HTTP_STATUS_CODE[response.status_code])

sub_account_list = response.json()

sub_account_id_list = [(i[0], i[1]) for i in sub_account_list]



###
# Step 4: switch into sub-account
###

for sub in sub_account_id_list:

    url = f"https://{current_user['active_brand_subdomain']}.eagleeyenetworks.com/g/aaa/switch_account"

    payload = { "account_id": sub[0] }
    headers = {'authorization': api_key }
    response = session.request("POST", url, data=payload, headers=headers)
    print("Switching to account: %s" % (sub[1]))
    # print("Step 4: %s" % HTTP_STATUS_CODE[response.status_code])


###
# Step 3: get list of devices
###

    url = f"https://{current_user['active_brand_subdomain']}.eagleeyenetworks.com/g/device/list"

    payload = ""
    headers = {'authorization': api_key }
    response = session.request("GET", url, data=payload, headers=headers)

    # print("Step 5: %s" % HTTP_STATUS_CODE[response.status_code])

    device_list = response.json()

    # filter everything but the bridges
    bridge_id_list = [{'id': i[1], 'guid': i[8], 'serial_number': i[9] } for i in device_list if i[3] == 'bridge']

    for bridge in bridge_id_list:
        print("ID: %s" % bridge['id'])
        print("GUID: %s" % bridge['guid'])
        print("serial number: %s" % bridge['serial_number'])
        print()

