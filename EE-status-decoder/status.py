#Usage: python device-status-example.py <auth_key>
#This application will use an already existing auth_key to query the devices
#and provide status information in the command line. This example shows how
#to properly parse device status from the /g/list/device API call and from
#websocket event updates
from pprint import pprint
import requests
import websocket
import json
import sys

#Constants for device list call array
DEVICE_ID_INDEX = 1
DEVICE_NAME_INDEX = 2
DEVICE_STATUS_INDEX = 10

#Bitmask recording
STATUS_BITMASK_ONLINE           = 0x100000
STATUS_BITMASK_ON               = 0x020000
STATUS_BITMASK_CAMERA_STREAMING = 0x040000
STATUS_BITMASK_VIDEO_RECORDING  = 0x080000

CLI_STATUS_STRING = "[{}] - Status Hex: {} - Status Clean: {}"

#Parse the auth_keys
# if len(sys.argv) != 2:
#     print "Usage: python2 {} <auth_key>".format(sys.argv[0])
#     sys.exit(-1)

auth_key=sys.argv[1]


#This function parses out the status in decimal format to a dictionary
#The dictionary has the keys (https://apidocs.eagleeyenetworks.com/#status-bitmask):
# - device_internet_online: Determines if the device is registered online to the cloud
# - camera_on: Determines if the camera is on
# - camera_streaming: Determines the bridge is actively streaming from the camera
# - camera_recording: Determines that the camera is actively recording
def parseStatusDecimal(status):
    ret = { 'device_internet_online': False,
            'camera_on': False,
            'camera_streaming': False,
            'camera_recording': False, }

    #Use bitmasking specified in https://apidocs.eagleeyenetworks.com/#status-bitmask
    #We use the bitmask operations to get the status from the integer. Each bit location
    #specifices a status for the camera.  For example, STATUS_BITMASK_ONLINE is equal to
    #0x100000 in hex which is b100000000000000000000 in binary. If the 21rst bit is enabled
    #in the status integer then that means the camera is online. You can get just that bit
    #through bit masking operations. In this case we do a bitmask AND operation to get each
    #status.
    ret['device_internet_online'] = bool(status & STATUS_BITMASK_ONLINE)
    ret['camera_on'] = bool(status & STATUS_BITMASK_ON)
    ret['camera_streaming'] = bool(status & STATUS_BITMASK_CAMERA_STREAMING)
    ret['camera_recording'] = bool(status & STATUS_BITMASK_VIDEO_RECORDING)

    return ret


#This function takes in a hexidecimal string and parses out the status
def parseStatusHex(status):
    #Convert the status hex string to decimal base 10 integer
    decimal_status = int(status, 16)
    return parseStatusDecimal(decimal_status)


#Get the list devices https://apidocs.eagleeyenetworks.com/#get-list-of-cameras
#The data structure returned is an array of arrays. The second dimensional array
#specifies properties of the device based on the index. For example, index 0 is
#the account id associated with the device. Index 3 specifies the type of device
#(camera or bridge). Index 10 is the status of the device in decimal format.
print("Status reported by /g/device/list")
resp = requests.get('https://login.eagleeyenetworks.com/g/device/list?A={}'.format(auth_key))
data = resp.json()
devices = []
for v in data:
    #We use parseStatusDecimal as the status is in base 10 decimal format
    ret = parseStatusDecimal(v[DEVICE_STATUS_INDEX])
    print(CLI_STATUS_STRING.format(v[DEVICE_ID_INDEX], hex(v[DEVICE_STATUS_INDEX]), ret))
    devices.append(v[DEVICE_ID_INDEX])

print
print

#Websockets are based on push events from the server. Establishing a websocket poll
#connection to the Eagle Eye API will give you event updates as they happen in real
#time. We will listen to event status changes for 10 seconds before exiting the 
#application.

#To connect to the API we need to know the account ID. We can get that information
#by doing an account list call (https://apidocs.eagleeyenetworks.com/#get-list-of-accounts)
resp = requests.get('https://login.eagleeyenetworks.com/g/account/list?A={}'.format(auth_key))
data= resp.json()
account_id = data[0][0]

#We create the websocket connection. Make sure we put in the auth_key in the HTTP
#Cookie attribute instead of passing it as a query parameter (A= in previous calls.
ws = websocket.WebSocket()
ws.connect('wss://login.eagleeyenetworks.com/api/v2/Device/{}/Events'.format(account_id), cookie='auth_key={}'.format(auth_key))

#Now that we have connected we need to send a JSON structure to tell the API what devices
#and events we are listening for (https://apidocs.eagleeyenetworks.com/#websocket-polling)
register_msg = { "cameras": {} }
for d in devices:
    register_msg['cameras'][d] = { 'resource': ['status'] }
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
    for device_id, device_data in jdata['data'].iteritems():
        ret = parseStatusDecimal(device_data['status'])
        print(CLI_STATUS_STRING.format(device_id, hex(device_data['status']), ret))

ws.close()

