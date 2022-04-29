import json
import requests
from .settings import *

# import the necessary packages
from imutils.video import VideoStream, FileVideoStream
from pyzbar import pyzbar
import argparse
import imutils
import time as t
import cv2

import requests

from datetime import datetime 
from datetime import timedelta

import logging
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.WARN)

class VideoAnalysis:
  def __init__(self, instance_obj={}):

    # breakout the common variables
    self.een = instance_obj['een']
    self.cam = instance_obj['cam']
    
    # go ahead and make the whole variable available
    self.instance_obj = instance_obj

    # each UUID will have itself as a key,
    # the value will be an object with last_annotation (timestamp)
    # and the EE annotation UUID (string)
    self.found_qr_codes = {}

    #######
    # MIN_DELAY_BETWEEN_ANNT, MAX_DELAY_BETWEEN_ANNT, TRACKER_HOST are variables in settings.py
    #######

    self.start_video()


  def post_annotation(self, cam, instance, ns, timestamp, obj):


    qr_code = obj['object']

    if qr_code in self.found_qr_codes:
      # we've seen this before
      pass
    else:
      # a QR code we haven't seen before
      logging.debug('First time we\'ve seen this QR code %s' % qr_code)
      self.found_qr_codes[qr_code] = {
        'last_annotation': datetime.utcnow(),
        'annt_uuid': None,
        'bounding_box': obj['_s']['b']
      }

    # check if inside of 9 seconds window from previous annotation
    # if so, make it a heartbeat type

    ts = self.een._EEN_timestamp_to_datetime(timestamp)

    interval = ts - self.found_qr_codes[qr_code]['last_annotation']

    interval = abs(interval.seconds)


    if  interval > MIN_DELAY_BETWEEN_ANNT:

      if self.found_qr_codes[qr_code]['annt_uuid'] != None  and interval < MAX_DELAY_BETWEEN_ANNT:
        logging.debug('update, last event was %s seconds ago' % interval)
        res = self.cam.update_annotation(instance=instance, ns=ns, timestamp=timestamp, obj=obj, annt_type='hb', uuid=self.found_qr_codes[qr_code]['annt_uuid'])
        
      else:
        # if not, make it a new annotation
        logging.debug('new annotation %s' % self.found_qr_codes[qr_code])
        res = self.cam.create_annotation(instance=instance, ns=ns, timestamp=timestamp, obj=obj)
        
      
      # update the annotation tracker
      self.found_qr_codes[qr_code]['last_annotation'] = ts

      if res and res['uuid']:
        self.found_qr_codes[qr_code]['annt_uuid'] = res['uuid']
        self.update_tracker(self.cam.camera_id, obj['object'], res['uuid'], timestamp)
        return res

      else:
        self.found_qr_codes[qr_code]['annt_uuid'] = None 
        
    else:
      # already working on this qr_code
      return None


  def update_tracker(self, camera_id=None, barcodeData=None, ee_uuid=None, timestamp=None):

    if camera_id and barcodeData and timestamp and ee_uuid:

      url = "%s/api/create_annotation/%s/%s/%s/%s/%s" % (TRACKER_HOST, barcodeData, camera_id, ee_uuid, timestamp, timestamp)

      res = requests.get(url)

      return res


  def start_video(self):
    # initialize the video stream and allow the camera sensor to warm up
    logging.info("Starting video stream...")  

    if self.instance_obj['vs_type'] == 'VideoStream':
      vs = VideoStream(self.instance_obj['vs']).start()

    if self.instance_obj['vs_type'] == 'CloudVideoStream':
      vs = VideoStream(self.instance_obj['vs']).start()

    if self.instance_obj['vs_type'] == 'RTSPVideoStream':
      vs = VideoStream(self.instance_obj['vs']).start()

    elif self.instance_obj['vs_type'] == 'FileVideoStream':
      vs = FileVideoStream(self.instance_obj['vs']).start()

    else:
      logging.error("Video Stream was not specified")
      return False

    # give the stream two seconds to warm up
    logging.debug("Waiting for the streams to get started...")
    t.sleep(2.0)


    # loop over the frames from the video stream
    while True:
        # grab the frame from the video stream and resize it to
        frame = vs.read()

        now = datetime.utcnow()
        now = self.een._datetime_to_EEN_timestamp(now)

        if frame is None:
            continue

        frame = imutils.resize(frame)

        height, width = frame.shape[:2]
        height = int(height)
        width = int(width)

        # find the barcodes in the frame and decode each of the barcodes
        barcodes = pyzbar.decode(frame)

        # loop over the detected barcodes
        for barcode in barcodes:
           # extract the bounding box location of the barcode and draw
           # the bounding box surrounding the barcode on the image
           (x, y, w, h) = barcode.rect
           cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

           # the barcode data is a bytes object so if we want to draw it
           # on our output image we need to convert it to a string first
           barcodeData = barcode.data.decode("utf-8")
           barcodeType = barcode.type

           # draw the barcode data and barcode type on the image
           text = "{} ({})".format(barcodeData, barcodeType)
           cv2.putText(frame, text, (x, y - 10),
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

           coord_X1 = float(x / width)
           coord_Y1 = float(y / height)
           coord_X2 = float((x + w) / width)
           coord_Y2 = float((y + h) / height)

           obj = {
            "object": barcodeData,
            "_s": {
              "b": [
                  [coord_X1, coord_Y1],
                  [coord_X2, coord_Y2]
                ]
              }
            }

           self.post_annotation(self.cam, self.een, 10020, now, obj)


        # Do not show the output frame in Docker,
        # good for debugging,
        # bad for performance and does not work in Docker
        
        # cv2.namedWindow(self.cam.name, cv2.WINDOW_NORMAL)
        # cv2.imshow(self.cam.name, frame)

        key = cv2.waitKey(1) & 0xFF

        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break

    logging.info("Cleaning up...")
    cv2.destroyAllWindows()
    vs.stop()
    return True
