
"""
Goes through cameras on the list of bridges
Set the cloud_retention_days to 60
Requires Python 3
Contact mcotton@een.com with questions
"""


from  EagleEye import *

een = EagleEye()


# Credentials to Eagle Eye account that can see the devices and has permission to change camera settings
USERNAME = ''
PASSWORD = ''


een.login(username=USERNAME, password=PASSWORD)

# array of bridge ESNs
site_bridges = ['']


# find cameras that are seen by these bridges, only looks at first bridge, but a good first pass
site_cameras = [i for i in een.cameras if i.bridges and i.bridges[0][0] in site_bridges]

# find cameras that are attached to these bridges
attd_cameras = [i for i in een.cameras if i.bridges and i.bridges[0][0] in site_bridges and i.bridges[0][1] == 'ATTD']

print( f"Total Bridges: {len(site_bridges)}" )
print( f"Total Cameras: {len(site_cameras)}" )
print( f"Total Cameras (Attached): {len(attd_cameras)}" )


for bridge in site_bridges:
    site_cameras = [i for i in een.cameras if i.bridges and i.bridges[0][0] in bridge]
    print( f"\n\nSite Bridge: {bridge}" )
    print( f"Site Cameras: {len(site_cameras)}" )
    for cam in site_cameras:
        cam._get_camera_parameters(een)
        if 'settings' in cam.camera_parameters:
            if 'cloud_retention_days' in cam.camera_parameters['settings']:

                if cam.camera_parameters['settings']['cloud_retention_days'] == 60:
                    print(f"-  {cam} has {cam.camera_parameters['settings']['cloud_retention_days']} days of cloud retention")
                else:
                    print(f"!!!{cam} has {cam.camera_parameters['settings']['cloud_retention_days']} days of cloud retention, setting it to 60 days now.\n\n")
                    cam.update_device_details(een, {"id": cam.camera_id, "camera_settings_add": json.dumps({ "settings": { "cloud_retention_days": 60 } } )  } ) 
                    cam._get_camera_parameters(een)
                    print(f"-  {cam} has {cam.camera_parameters['settings']['cloud_retention_days']} days of cloud retention")
            else:
                print(f"Couldn't get cloud_retention_days for {cam}")
        else:
            print(f"Couldn't get settings for {cam}")






