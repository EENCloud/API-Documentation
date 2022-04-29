from flask import Flask
from flask import flash, redirect, render_template, request, session 
from flask import abort, url_for, send_file, send_from_directory, jsonify

import os
from functools import wraps

from werkzeug.utils import secure_filename

from openpyxl import Workbook
from openpyxl import load_workbook

import requests
import json

import pytz
from pytz import timezone

from datetime import datetime, timedelta

import redis
db = redis.StrictRedis(host="db", decode_responses=True)


from EagleEye import * 

een_sessions = {}
 
app = Flask(__name__)



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

 
@app.route('/')
def home():
    if not session.get('logged_in'):
        return redirect('/login')
    else:
        een = een_sessions[session['id']]

        ret_obj = {}

        ret_obj['cameras'] = [i.to_dict() for i in een.cameras]
        ret_obj['esns'] = [i.camera_id for i in een.cameras if i.camera_id is not None]

        return render_template('index.html', template_values=ret_obj)
 

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
    return do_admin_login()



@app.route('/camera/<esn>/<start_timestamp>/<end_timestamp>')
@app.route('/camera/<esn>')
@login_required
def camera_details(esn, start_timestamp=None, end_timestamp=None):

    ret_obj = {}

    een = een_sessions[session['id']]
    cam = een.find_by_esn(esn)
    
    if start_timestamp == None or end_timestamp == None:
        twenty_four_hours = timedelta(hours=24)
        start_timestamp = een._datetime_to_EEN_timestamp(datetime.utcnow() - twenty_four_hours)
        end_timestamp = een._datetime_to_EEN_timestamp(datetime.utcnow())
        

    if cam:
        cam.get_video_list(instance=een, start_timestamp=start_timestamp, end_timestamp=end_timestamp, options='coalesce')
    
        ret_obj['user'] = een.user
        ret_obj['camera'] = cam.to_dict()
        ret_obj['videos'] = [(i[0],\
                            i[1], \
                            een._EEN_timestamp_to_datetime(convert_timezone(een, cam, i[0])),\
                            een._EEN_timestamp_to_datetime(convert_timezone(een, cam, i[1])),\
                            een._EEN_timestamp_to_datetime(convert_timezone(een, cam, i[1]))
                                - een._EEN_timestamp_to_datetime(convert_timezone(een, cam, i[0])))\
                            for i in cam.videos]


        # automatically call prefetch on every video
        # for i in cam.videos:
        #     prefetch_video(esn, i[0], i[1])


    else:
        return render_template('404.html')

    return render_template('camera_details.html', template_values=ret_obj)



@app.route('/prefetch_video/<esn>/<start_timestamp>/<end_timestamp>')
@login_required
def prefetch_video(esn, start_timestamp, end_timestamp):
    een = een_sessions[session['id']]
    cam = een.find_by_esn(esn)
    auth_key = een_sessions[session['id']].session.cookies['auth_key']

    success_hook = f"https%3A//prefetch.een.cloud/webhook/success/{cam.camera_id}"
    failure_hook = f"https%3A//prefetch.een.cloud/webhook/failure/{cam.camera_id}"

    uuid = cam.prefetch_video(instance=een, start_timestamp=start_timestamp, end_timestamp=end_timestamp, success_hook=success_hook, failure_hook=failure_hook)

    db.hmset(f"{esn}:{start_timestamp}-{end_timestamp}",{
            'uuid': str(uuid),
            'status': str('requested'),
            'category': str(''),
            'auth_key': str(auth_key)
        })

    db.sadd(f"pending:{esn}", f"{esn}:{start_timestamp}-{end_timestamp}")
    db.incr("pending")


    return jsonify(esn)



@app.route('/webhook/<category>/<esn>', methods=['GET', 'POST'])
@app.route('/webhook/<category>', methods=['GET', 'POST'])
def handle_webhook(category=None, esn=None):

    print('Webhook callback for %s %s: %s' % (category, esn, request.json))

    try:
        start_timestamp = request.json['data'][0]['arguments']['start_timestamp']
        end_timestamp = request.json['data'][0]['arguments']['end_timestamp']
        esn = request.json['data'][0]['arguments']['id']
        uuid = request.json['data'][0]['uuid']
    except TypeError:
        print("Webhook request without POST data")
        return json.dumps("{}")

    if start_timestamp and end_timestamp and esn and uuid:

        if category == 'success':
            db.smove(f"pending:{esn}", f"success:{esn}", f"{esn}:{start_timestamp}-{end_timestamp}")
            db.incrby("success", "1")
            db.incrby("pending", "-1")
            db.hmset(f"{esn}:{start_timestamp}-{end_timestamp}",{
                'uuid': str(uuid),
                'status': str('returned'),
                'category': str('success'),
                'data': json.dumps(request.json)
            })

        elif category == 'failure':
            db.smove(f"pending:{esn}", f"failure:{esn}", f"{esn}:{start_timestamp}-{end_timestamp}")
            db.incrby("failure", "1")
            db.incrby("pending", "-1")
            db.hmset(f"{esn}:{start_timestamp}-{end_timestamp}",{
                'uuid': str(uuid),
                'status': str('returned'),
                'category': str('failure'),
                'data': json.dumps(request.json)
            })

    else:

        return json.dumps("")



    return json.dumps(request.json)




@app.route('/counter/<esn>')
@login_required
def get_counter(esn=None):


    pending = db.get('pending')
    failure = db.get('failure')
    success = db.get('success')

    ret = {
        'pending': pending or 0,
        'failure': failure or 0,
        'success': success or 0,
        'successful': [i for i in db.keys(f"{esn}*") if db.hgetall(i)['category'] =='success'] ,
        'failed': [i for i in db.keys(f"{esn}*") if db.hgetall(i)['category'] =='failure']
    }


    return jsonify(ret)






def convert_timezone(een, cam, ee_timestamp):

    #convert it to a DateTime object
    timestamp = een._EEN_timestamp_to_datetime(ee_timestamp)
    
    # convert it to UTC
    utc = pytz.timezone('UTC')
    utc_time = utc.localize(timestamp)

    # convert it to camera's timezone
    local_tz = pytz.timezone(cam.timezone)
    local_time = utc_time.astimezone(local_tz)

    # convert it back to een timestamp
    out_time = een._datetime_to_EEN_timestamp(local_time)
    return out_time



if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True,host='0.0.0.0', port=4000,  threaded=True)
