from flask import Flask
from flask import flash, redirect, render_template, request, session, Response
from flask import abort, url_for, send_file, send_from_directory

import os
import json
import datetime
from functools import wraps
from werkzeug.utils import secure_filename

from datetime import datetime, timedelta
import pytz

import requests
import json
import base64

import logging

from settings import *


from EagleEye import EagleEye
een = EagleEye()
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

        if session.get('logged_in') != True:
            print("user is not logged_in or doesn't have a session id")
            if request.is_json:
                # if they are hitting the API, give them a 401
                print("sending them a 401")
                return Response("{}", status=401, mimetype='application/json')
            else:
                # if not, show them the login page
                print("redirecting to /login")
                return redirect('/login')


        return f(*args, **kwargs)
    return decorated_function


@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/login', methods=['GET', 'POST'])
def do_admin_login():
    if request.method == 'GET':
        return render_template('login.html')

    global een

    if request.method == 'POST':
        if 'id' in session:
            
            if session['id'] in een_sessions:
                een = een_sessions[session['id']]

            else:
                een_sessions[session['id']] = een 
        else:
            session['id'] = os.urandom(16)
            een_sessions[session['id']] = een


        #print("calling een.login")        
        print(f"Login attempt for {request.form['username']}")
        if een.login(username=request.form['username'], password=request.form['password']):
            session['logged_in'] = True
            session['name'] = f"{een.user['first_name']} {een.user['last_name']}"
            
        else:
            flash('wrong password!')
            return redirect('/bad_password')
        
        return redirect('/')


@app.route("/bad_password")
def login_with_bad_password():
    return render_template("bad_password.html", template_values={})
    


@app.route("/logout")
@login_required
def logout():
    session['logged_in'] = False
    session['name'] = ''
    
    if een_sessions and 'session' in een_sessions and 'id' in session and session['id'] is not None:
        if een_sessions[session['id']]:
            try:
                del een_sessions[session['id']]
            except KeyError:
                pass
    
    session['id'] = None
    return redirect('/login')


@app.route("/2x2")
@app.route("/")
@login_required
def hello():
    if een and een.user:

        ret = {
                "options": {},
                "username": een.user['first_name'] + ' ' + een.user['last_name'],
                "cameras": sorted([(i.name, i.camera_id) for i in een.cameras if i.camera_id and i.name]),
                "auth_key":  een.session.cookies['auth_key']
            }

        
        return render_template("index.html", template_values=ret)
    else:
        return redirect('/login')


@app.route("/3x3")
@login_required
def hello3x3():
    if een and een.user:

        ret = {
                "options": {},
                "username": een.user['first_name'] + ' ' + een.user['last_name'],
                "cameras": sorted([(i.name, i.camera_id) for i in een.cameras if i.camera_id and i.name]),
                "auth_key":  een.session.cookies['auth_key']
            }

        
        return render_template("3x3.html", template_values=ret)
    else:
        return redirect('/login')


@app.route("/4x4")
@login_required
def hello4x4():
    if een and een.user:

        ret = {
                "options": {},
                "username": een.user['first_name'] + ' ' + een.user['last_name'],
                "cameras": sorted([(i.name, i.camera_id) for i in een.cameras if i.camera_id and i.name]),
                "auth_key":  een.session.cookies['auth_key']
            }

        
        return render_template("4x4.html", template_values=ret)
    else:
        return redirect('/login')


@app.template_filter()
def EE_date(text, camera_id=None):
    if camera_id:
        cam = een.find_by_esn(camera_id)
        
        if cam:
            #convert it to a DateTime object
            timestamp = een._EEN_timestamp_to_datetime(text)
    
            # convert it to UTC
            utc = pytz.timezone('UTC')
            utc_time = utc.localize(timestamp)

            # convert it to camera's timezone
            local_tz = pytz.timezone(cam.timezone)
            local_time = utc_time.astimezone(local_tz)

            # convert it back to een timestamp
            # out_time = een._datetime_to_EEN_timestamp(local_time)
            return local_time.strftime('%Y-%m-%d %H:%M:%S %Z')
            
            # dt = een._EEN_timestamp_to_datetime(text)
            # local_tz = pytz.timezone(cam.timezone)
            
            # return local_tz.localize(dt).strftime('%Y-%m-%d %H:%M:%S %Z')

    dt = een._EEN_timestamp_to_datetime(text)
    return dt


@app.template_filter()
def clean_up(text):
    if text:
        text = text.replace('_', ' ')
        results = [i.capitalize() for i in text.split(' ')]
        text = ' '.join(results)
    
    return text



if __name__ == "__main__":
    app.secret_key = os.urandom(128)
    # replace this with your own secret

    app.run(threaded=True, debug=False, host='0.0.0.0', port=3000)


