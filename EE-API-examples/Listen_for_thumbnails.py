import websocket
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
# Step 3: get list of devices
###

url = f"https://{current_user['active_brand_subdomain']}.eagleeyenetworks.com/g/device/list"

payload = ""
headers = {'authorization': api_key }
response = session.request("GET", url, data=payload, headers=headers)

print("Step 3: %s" % HTTP_STATUS_CODE[response.status_code])

device_list = response.json()

# filter everything but the cameras
camera_id_list = [i[1] for i in device_list if (i[3] == 'camera' and i[0] != None)]



###
# Step 4: subscribe to websocket pollstream
# listening for thumbnail events
###


#Websockets are based on push events from the server. Establishing a websocket poll
#connection to the Eagle Eye API will give you event updates as they happen in real
#time. 

#To connect to the API we need to know the account ID. We can get that information
#from the user object returned after a successful login in Step 2


auth_key = session.cookies.get_dict()['auth_key']
account_id = current_user['owner_account_id']

#We create the websocket connection. Make sure we put in the auth_key in the HTTP
#Cookie attribute instead of passing it as a query parameter (A= in previous calls.
ws = websocket.WebSocket()
ws.connect(f"wss://{current_user['active_brand_subdomain']}.eagleeyenetworks.com/api/v2/Device/{account_id}/Events", cookie=f"auth_key={auth_key}")

#Now that we have connected we need to send a JSON structure to tell the API what devices
#and events we are listening for (https://apidocs.eagleeyenetworks.com/#websocket-polling)
register_msg = { "cameras": {} }
for d in camera_id_list:
    register_msg['cameras'][d] = { 'resource': ['event'], 'event': ['PRTH'] }
    data = json.dumps(register_msg)

#Send the register event data structure to the API
print("Registering for status events {}".format(data))
ws.send(data)

#Now we continue to recieve information as the API will push
#any new status changes for the cameras we have registered to
#observe status change events.
while True:
    data = ws.recv()
    jdata = json.loads(data) #convert the json string to a python dictionary/array
    for device_id in jdata['data']:
        print('{} has a new thumbnail at {}'.format(device_id, jdata['data'][device_id]['event']['PRTH']['timestamp']))

ws.close()



