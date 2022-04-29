from flask import Flask
from flask import flash, redirect, render_template, request, session 
from flask import abort, url_for, send_file, send_from_directory

import os
from functools import wraps

from werkzeug.utils import secure_filename

import requests

import json

import shutil
import subprocess

from EagleEye import *

een = EagleEye()
 
app = Flask(__name__)


 
@app.route('/')
def home():
    file_list = os.listdir('tmp')
    file_list.sort()
    return render_template('index.html',  file_list=file_list )



@app.route('/api/download/<path:filename>')
def download(filename):
    return send_from_directory(directory='./tmp', filename=filename)
 


@app.route('/api/pull_frame/<device_id>/<start_timestamp>/<auth_key>', methods=['GET'])
def pull_frame(device_id, start_timestamp, auth_key):

    end_timestamp = EagleEye._datetime_to_EEN_timestamp(\
        EagleEye._EEN_timestamp_to_datetime(start_timestamp) + timedelta(seconds=2))

    url = f"https://login.eagleeyenetworks.com/asset/play/video.flv?id={device_id}&start_timestamp={start_timestamp}&end_timestamp={end_timestamp}&A={auth_key}"
    print(url)
    


    print('checking if we need to pull_frame request')

    tmp_filename = f"tmp/{device_id}-{start_timestamp}.jpg"
    
    try:
        statinfo = os.stat(tmp_filename)
        return json.dumps({ 
                                    'proxy_status_code': None, 
                                    'ffmpeg_return_code ': None,
                                    'link_to_download': f"/api/download/{device_id}-{start_timestamp}.jpg" })

    except FileNotFoundError:
    
        print('making pull_frame request')
        res = requests.get(url, stream=True)
        print('finished pull_frame request')
    
        print(f"fetch_video got a {res.status_code}")

        if res.status_code == 200:
            # create a filename
            # save response to file
            # redirect to the URL serving the file
            # ???

            local_filename = f"flv/{device_id}-{start_timestamp}.flv"

            with open(local_filename, 'wb') as f:
                shutil.copyfileobj(res.raw, f)
                print(f"Done copying the the response into file: {local_filename}")

            cmd_string = f"ffmpeg -i {local_filename} -ss 00.00 -vframes 1 -y tmp/{device_id}-{start_timestamp}.jpg"
            print(f"calling ffmpeg command: {cmd_string}")

            cmd = subprocess.run(cmd_string.split(" "))

            if cmd.returncode == 0:
                print('FFPEG returned 0')
                return json.dumps({ 
                                    'proxy_status_code': res.status_code, 
                                    'ffmpeg_return_code ': cmd.returncode,
                                    'link_to_download': f"/api/download/{device_id}-{start_timestamp}.jpg" })
            else:
                # handle error
                print('FFMPEG returned :', cmd.returncode)



    return json.dumps({ 'status': 'Failed', 'proxy_status_code': res.status_code })



if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True,host='0.0.0.0', port=4000)
