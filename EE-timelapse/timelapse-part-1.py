
import sys

from EagleEye import *

een = EagleEye()

# login credentials
USERNAME = ""
PASSWORD = ""

if USERNAME == "" or PASSWORD == "":
    print("Update script with your credentials")
    sys.exit()

# which camera are we accessing
CAMERA_ESN = ""
if CAMERA_ESN == "":
    print("Update script with the camera's ESN")
    sys.exit()

# what time range are we looking for
START_TIME = ""
END_TIME = ""

if START_TIME == "" or END_TIME == "":
    print("Update script with a start and end time")
    sys.exit()

# total length of the video in seconds
VIDEO_LENGTH = 600


een.login(username=USERNAME, password=PASSWORD) 

this_camera = een.find_by_esn(CAMERA_ESN) 

this_camera.get_preview_list(instance=een, start_timestamp=START_TIME, end_timestamp=END_TIME, asset_class="pre") 


# Figure out how to get to the desired video length assuming input at 10 FPS.
# Get the total number of images devides by the desired video length in seconds.
# The result is how man images we need to skip in order to represent the time period.
number_of_previews = len(this_camera.previews)
steps = number_of_previews / VIDEO_LENGTH

import math
steps = math.ceil(steps)

print( f"Total images: {number_of_previews}" )
print( f"Length of video: {VIDEO_LENGTH}" )
print( f"Steps: {steps}" )

# Only download the iamges that are going to be used.
for pre in sorted(this_camera.previews)[0::steps]:
    img = this_camera.download_image(instance=een, timestamp=pre, asset_class="pre")
    if img:
        local_filename = f"tmp/{this_camera.camera_id}-{pre}.jpg"
        open(local_filename, 'wb').write(img)
    else: 
        print(f"{local_filename} failed")



# Let's go ahead and call ffmpeg to make the images into a movie
# Assumes that you've got ffmpeg installed or are using the included Docker container

import subprocess

subprocess.run(["ffmpeg", "-framerate", "10", "-pattern_type", "glob", "-i", f"tmp/{CAMERA_ESN}-*.jpg", "-y", "-r", "30", "-pix_fmt", "yuv420p", f"tmp/{CAMERA_ESN}.mp4"])
