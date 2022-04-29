
"""
Goes through cameras on the list of bridges
Changes the transmit modes for preview and video
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
site_bridges = []


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
        if 'camera_parameters' in cam.camera_parameters:
            if 'user_settings' in cam.camera_parameters['camera_parameters']:
                if 'settings' in cam.camera_parameters['camera_parameters']['user_settings']:
                    if 'preview_transmit_mode' in cam.camera_parameters['camera_parameters']['user_settings']['settings']:
                        if cam.camera_parameters['camera_parameters']['user_settings']['settings']['preview_transmit_mode'] == 'always':
                            pass
                        else:
                            print( f" -updating preview settings for {cam}")
                            cam.update_device_details(een, {"id": cam.camera_id, "camera_settings_add": json.dumps({ "settings": { "preview_transmit_mode": "always" } } )  })

                    if 'video_transmit_mode' in cam.camera_parameters['camera_parameters']['user_settings']['settings']:
                        if cam.camera_parameters['camera_parameters']['user_settings']['settings']['video_transmit_mode'] == 'background':
                            pass
                        else:
                            print( f" -updating video settings for {cam}")
                            cam.update_device_details(een, {"id": cam.camera_id, "camera_settings_add": json.dumps({ "settings": { "video_transmit_mode": "background" } } )  })

                    if 'preview_transmit_mode' in cam.camera_parameters['camera_parameters']['user_settings']['settings'] and 'video_transmit_mode' in cam.camera_parameters['camera_parameters']['user_settings']['settings']:
                        cam._get_camera_parameters(een)
                        print(f"{cam}")
                        print(f"-  {cam} has preview_transmit_mode: {cam.camera_parameters['camera_parameters']['user_settings']['settings']['preview_transmit_mode']} ")
                        print(f"-  {cam} has video_transmit_mode: {cam.camera_parameters['camera_parameters']['user_settings']['settings']['video_transmit_mode']} ")

                else:
                    print(f" finding settings failed for {cam}")
            else:
                print(f" finding user_settings failed for {cam}")
        else:
            print(f" finding camera_parameters failed for {cam}")







