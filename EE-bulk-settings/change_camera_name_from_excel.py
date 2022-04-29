
"""
Match up Eagle Eye caneras by IP address with a spreadsheet of camera names.
Apply tag to all attached cameras (on specified bridges) even if they aren't in the spreadsheet
Requires Python 3
Contact mcotton@een.com with questions
"""


from  EagleEye import *

een = EagleEye()


# Credentials to Eagle Eye account that can see the devices and has permission to change camera settings
USERNAME = ''
PASSWORD = ''
SPREADSHEET = 'file.xlsx'

# Define which colument in spreadsheet contains data
SOURCE_NAME = 12
SOURCE_IP = 4

een.login(username=USERNAME, password=PASSWORD)

# array of bridge ESNs
site_bridges = ['']

# find cameras that are seen by these bridges, only looks at first bridge, but a good first pass
site_cameras = [i for i in een.cameras if i.bridges and i.bridges[0][0] in site_bridges]

# find cameras that are attached to these bridges
attd_cameras = [i for i in een.cameras if i.bridges and i.bridges[0][0] in site_bridges and i.bridges[0][1] == 'ATTD']



from openpyxl import load_workbook


wb = load_workbook(SPREADSHEET)
ws = wb.active

for row in ws.rows: 
    item = een.find_by_ip(row[SOURCE_IP].value)
    if item:
        if item.name is not row[SOURCE_NAME].value:
            print( f"Camera at ip {row[SOURCE_IP].value} is named {item.name} and should be named {row[SOURCE_NAME].value}")
            if item.camera_id:

                if 'ord' not in item.tags[0]:
                    print( f"{row[SOURCE_NAME].value} could not find ord tag on {item.camera_id}" )
                    item.tags[0].append('ord')
                else:
                    print( f"{row[SOURCE_NAME].value} already has ord tag" )

                if item.name != row[SOURCE_NAME].value:
                    print( f"Camera name doesn't match spreadsheet going to send {item.camera_id} and {row[SOURCE_NAME].value}")
                    item.update_device_details(instance=een, body={'id': item.camera_id, 'name': row[SOURCE_NAME].value, 'tags': item.tags[0] })
                else:
                    print( f"Camera {item.camera_id} already has it's name set, skipping" )

            else:
                print( f"need to have an id in POST body")
        else:
            print( f"Camera at ip {row[SOURCE_IP].value} is already naemd {item.name}, no need to change it")




# loop through all attached cameras, not just matching the spreadsheet, and set the 'ord' tag

for item in attd_cameras:
    if 'ord' not in item.tags[0]:
        print( f"could not find ord tag on {item.camera_id}" )
        item.tags[0].append('ord')
        print( f"Camera name doesn't match spreadsheet going to send {item.camera_id}")
        tem.update_device_details(instance=een, body={'id': item.camera_id, 'tags': item.tags[0] })





