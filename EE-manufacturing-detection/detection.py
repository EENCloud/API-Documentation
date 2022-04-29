

################################
#                              #
# Eagle Eye Networks           #
#                              #
################################




from EagleEye import * 
een = EagleEye()

from VideoAnalysis import *

# pull in user settings
from settings import *

import logging
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.WARNING)

import multiprocessing as mp





if __name__ == '__main__':
  mp.set_start_method('spawn')

  #######
  # EEN_USERNAME and EEN_PASSWORD are variables inside of settings.py
  #######
  een.login(username=EEN_USERNAME, password=EEN_PASSWORD)
  
  processes = []

  
  #######
  # EEN_CAMERAS is a variable inside os settings.py
  #######
  
  for item in EEN_CAMERAS:
    cam = een.find_by_esn(item['id'])

    item['cam'] = cam
    item['een'] = een

    ######
    # This will create the URLs to stream video from the cloud,
    # if you are using RTSP or local files, replace this with
    # the correct strings
    ######

    if 'vs' not in item:
      item['vs'] = "".join([
                    een.host,
                    "/asset/play/video.flv",
                    "?id=",
                    item['id'],
                    "&start_timestamp=",
                    "stream_",
                    een.user['id'],
                    item['id'],
                    "&end_timestamp=",
                    "+300000",
                    "&A=",
                    een.auth_key
                  ])

      logging.debug(item['vs'])

    p = mp.Process(target=VideoAnalysis, args=(item,))
    logging.info(f"Starting process for {item['id']} ")
    
    p.start()
    processes.append(p)

  for i in processes:
    i.join()








