
"""
Goes through cameras on the list of bridges
Set the camera bitrate to 2000mpbs
Requires Python 3
Contact mcotton@een.com with questions
"""


from  EagleEye import *

een = EagleEye()


# Credentials to Eagle Eye account that can see the devices and has permission to change camera settings
USERNAME = ''
PASSWORD = ''


een.login(username=USERNAME, password=PASSWORD)


site_bridges = een.bridges


# find cameras that are seen by these bridges, only looks at first bridge, but a good first pass
site_cameras = [i for i in een.cameras if i.bridges and i.bridges[0][0] in site_bridges]

# find cameras that are attached to these bridges
attd_cameras = [i for i in een.cameras if i.bridges and i.bridges[0][0] in site_bridges and i.bridges[0][1] == 'ATTD']

print( f"Total Bridges: {len(site_bridges)}" )
print( f"Total Cameras: {len(site_cameras)}" )
print( f"Total Cameras (Attached): {len(attd_cameras)}" )

list_of_esns = []

site_cameras = []

for i in list_of_esns:
    cam = een.find_by_esn(i)
    site_cameras.append(cam)

print(f"site_cameras: {len(site_cameras)}")


def run(site_cameras):

    for cam in site_cameras:
            cam._get_camera_parameters(een)
            if 'camera_parameters' in cam.camera_parameters:
                if 'active_settings' in cam.camera_parameters['camera_parameters']:
                    if 'video_bandwidth_factor' in cam.camera_parameters['camera_parameters']['active_settings']:

                        if cam.camera_parameters['camera_parameters']['active_settings']['video_bandwidth_factor']['v'] == 2:
                            print(f"{cam.camera_id} video_bandwidth_factor {cam.camera_parameters['camera_parameters']['active_settings']['video_bandwidth_factor']['v']}")
                        else:
                            print(f"{cam.camera_id} needs to be changed")
                            cam.update_device_details(een, {"id": cam.camera_id, "camera_settings_add": json.dumps({ "settings": { "video_bandwidth_factor": 2 } } )  } )
                    else:
                        print(f"Couldn't get video_bandwidth_factor for {cam}")
                else:
                    print(f"Couldn't get active_settings for {cam}")
            else:
                print(f"Couldn't get camera_parameters for {cam}")


