from flask import Flask
from flask import flash, redirect, render_template, request, session 
from flask import abort, url_for, send_file, send_from_directory

import os
from functools import wraps
from werkzeug.utils import secure_filename

from datetime import datetime, timedelta
import pytz

import requests
import json

import logging

from settings import secret_key

from EagleEye import * 

een_sessions = {}
 
app = Flask(__name__)

if secret_key:
    app.secret_key = secret_key
else:
    app.secret_key = os.urandom(128)

app.config['SESSION_TYPE'] = 'filesystem'


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return render_template('login.html')
        return f(*args, **kwargs)
    return decorated_function


@app.route('/static/<path:filename>')
def send_static_files(filename):
    return send_from_directory('static/', filename)

 
@app.route('/', methods=['GET', 'POST'])
def home():
    if not session.get('logged_in'):
        return redirect('/login')
    else:

        if request.method == 'GET':
            if session['id'] in een_sessions:
                een = een_sessions[session['id']]
                return render_template('index.html', cameras=een.cameras, results={}, params=None)
            else:
                # server mush have restarted, clear een_sessions
                session.clear()
                return redirect('/login')

        if request.method == 'POST':
            esn = request.form.get('esn')
            start_timestamp = request.form.get('start_time').replace('-','') + '000000.000' 
            end_timestamp = request.form.get('end_time').replace('-','') + '235959.999' 

            params = {
                "esn": esn,
                "start_time": request.form.get('start_time'),
                "end_time": request.form.get('end_time')
            }

            een = een_sessions[session['id']]
            camera = een.find_by_esn(esn)
            camera.get_cloud_video_list(instance=een, start_timestamp=start_timestamp, end_timestamp=end_timestamp)

            return render_template('index.html', cameras=[i for i in een.cameras if i.camera_id is not None], results=camera, params=params)
 
@app.route('/login', methods=['GET', 'POST'])
def do_admin_login():
    if request.method == 'GET':
        if not session.get('logged_in'):
            return render_template('login.html')
        else:
            return redirect('/')

    if request.method == 'POST':
        if 'id' in session:
            
            if session['id'] in een_sessions:
                een = een_sessions[session['id']]

            else:
                een = EagleEye()
                een_sessions[session['id']] = een 
        else:
            session['id'] = os.urandom(16)
            een = EagleEye()
            een_sessions[session['id']] = een

        
        if een.login(username=request.form['username'], password=request.form['password']):
            session['logged_in'] = True
            session['name'] = f"{een.user['first_name']} {een.user['last_name']}"    
            
        else:
            flash('wrong password!')
        
        return redirect('/')
 
@app.route("/logout")
def logout():
    session['logged_in'] = False
    session['name'] = ''
    
    if 'id' in session and session['id'] is not None:
        if een_sessions[session['id']]:
            del een_sessions[session['id']]
    
    session['id'] = None
    return home()
 

@app.route('/generate', methods=['GET', 'POST'])
@login_required
def generate_data():
    if request.method == 'GET':
        een = een_sessions[session['id']]
        return render_template('devices.html', cameras=een.cameras)

    if request.method == 'POST':
        esn = request.form.get('esn')
        start_timestamp = request.form.get('start_time').replace('-','') + '000000.000' 
        end_timestamp = request.form.get('end_time').replace('-','') + '235959.999' 

        een = een_sessions[session['id']]
        camera = een.find_by_esn(esn)
        camera.get_video_list(instance=een, start_timestamp=start_timestamp, end_timestamp=end_timestamp, options='coalesce')

        wb = Workbook()
        ws = wb.active

        for video in camera.videos:
            ws.append([camera.camera_id, video[0], video[1]])

        filename = f"./uploads/{esn}-{start_timestamp}.xlsx"
     
        wb.save(filename)

        return send_file(filename, as_attachment=True)


@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)

        f = request.files['file']
        location = secure_filename(f.filename)
        f.save('./uploads/' + location)
        return redirect('/excel/view/%s' % location, code=302)


@app.route('/view/<path:filename>', methods=['GET'])
@login_required
def view(filename):
    wb = load_workbook('./uploads/' + filename)
    ret_obj = {
        'esns': {},
        'een': een_sessions[session['id']]
    }

    if wb:
        ws = wb.active

        for row in ws.iter_rows(row_offset=2):
            esn = row[0].value
            start = row[1].value
            end = row[2].value

            if esn:
                if esn in ret_obj['esns']:
                    ret_obj['esns'][esn].append(
                        {
                            'start_timestamp': start,
                            'end_timestamp': end
                        }   
                    )
                else:
                    ret_obj['esns'][esn] = [{
                        'start_timestamp': start,
                        'end_timestamp': end
                    }]

    return render_template('upload.html', template_values=ret_obj)


@app.route('/api/get_info/<device_id>/<start_timestamp>/<end_timestamp>', methods=['GET'])
@login_required
def get_info(device_id, start_timestamp, end_timestamp):
    auth_key = een_sessions[session['id']].session.cookies['auth_key']
    url = f"https://login.eagleeyenetworks.com/asset/info/video?id={device_id}&start_timestamp={start_timestamp}&end_timestamp={end_timestamp}&A={auth_key}"
    print(url)
    print(auth_key)

    print('making get_info request')
    res = requests.get(url)
    print('finishing get_info request')

    print(f"get_info got a {res.status_code}")

    if res.status_code == 200:

        if res.text:
            return res.text


    return json.dumps({ 'proxy_status_code': res.status_code })





if __name__ == "__main__":
    # app.secret_key = os.urandom(12)
    app.run(threaded=True, debug=True, host='0.0.0.0', port=3000)
