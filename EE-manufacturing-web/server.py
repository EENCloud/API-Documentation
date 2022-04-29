from flask import Flask
from flask import flash, redirect, render_template, request, session, Response
from flask import abort, url_for, send_file, send_from_directory
from flask import jsonify

import os
import datetime
from functools import wraps
from werkzeug.utils import secure_filename

from datetime import datetime, timedelta
import pytz

import requests
import json
import base64

from sqlalchemy import exc

import logging
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.WARNING)

from models import *
from settings import *


from EagleEye import * 
een = EagleEye()
een_sessions = {}
 

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////app/tmp/test.db'

db.app = app
db.init_app(app)
db.create_all()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        if session.get('logged_in') != True:
            logging.debug("user is not logged_in or doesn't have a session id")
            if request.is_json:
                # if they are hitting the API, give them a 401
                logging.debug("sending them a 401")
                return Response("{}", status=401, mimetype='application/json')
            else:
                # if not, show them the login page
                logging.debug("redirecting to /login")
                return redirect('/login')


        return f(*args, **kwargs)
    return decorated_function







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


        logging.debug("calling een.login")        
        if een.login(username=request.form['username'], password=request.form['password']):
            session['logged_in'] = True
            session['name'] = f"{een.user['first_name']} {een.user['last_name']}"


            has_credentials = Credentials.query.filter_by(username=request.form['username']).first()
            if has_credentials == None:            
                new_user = Credentials(
                        username = request.form['username'],
                        password = request.form['password'],
                        account_id = een.user['owner_account_id']
                    )
                db.session.add(new_user)
                db.session.commit()

            # pull user's devices
            logging.debug(f"checking for new cameras: {een.cameras}")
            for camera in een.cameras:
                if camera.camera_id:
                    camera_exists = Cameras.query.filter_by(camera_id=camera.camera_id).first()
                    if camera_exists == None:
                        try:
                            # camera needs to be added
                            new_camera = Cameras(
                                    camera_id = camera.camera_id,
                                    account_id = een.user['owner_account_id'],
                                    camera_name = camera.name
                                )
                            db.session.add(new_camera)
                            db.session.commit()
                        except exc.IntegrityError as e:  
                            logging.debug(f"caught an exception {e}")  
                            db.session.rollback()
                        except exc.OperationalError as e:
                            logging.debug(f"caught an exception {e}")  
                            db.session.rollback()
                    else:
                        # camera already exists
                        pass
                else:
                    # camera is not added and doesn't have an ID yet
                    pass

        else:
            flash('wrong password!')
        
        return redirect('/')



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





@app.route("/")
@login_required
def hello():
    if een and een.user:
        ret = {}

        ret['qrcodes'] = [i.to_dict() for i in QRCodes.query.all()]

        return render_template("index.html", template_values=ret)
    else:
        return redirect('/login')




@app.route("/qrcode/<qr_code_id>")
def details(qr_code_id):
    if een and een.user:
        ret = {}

        qr = QRCodes.query.get(qr_code_id)

        if qr:
            ret['qrcodes'] = qr.to_dict()
            ret['host'] = een.host
            return render_template('details.html', template_values=ret)
        

        else:
            return render_template('404.html', template_values={})
        
    else:
        return redirect('/login')





@app.route("/api/create_annotation/<qr_code>/<camera_id>/<EE_uuid>/<EE_starttime>/<EE_endtime>")
def create_annotation(qr_code, camera_id, EE_uuid, EE_starttime, EE_endtime):
    
    ret = {}

    # find the right QRCode
    q = QRCodes.query.filter_by(value=qr_code).first()

    if q == None:
        # create a new QRCode from the uuid passed in
        q = QRCodes(value=qr_code, description="", image_location=str('tmp/' + qr_code + '.png'))

        # create a QR code image for this mystery code
        generate_qrcode(id=qr_code)
    
        db.session.add(q)
        db.session.commit()

    q.annotations.append(Annotations(camera_id=camera_id, EE_starttime=EE_starttime, EE_endtime=EE_endtime, EE_uuid=EE_uuid))
    

    # save it to the db
    db.session.add(q)
    db.session.commit()

    return jsonify(ret)


@app.route("/api/generate/<id>")
@app.route("/api/generate")
def generate_qrcode(id=None):
    import pyqrcode
    import uuid
    import io

    if id:
        uuid_filename = str(id)

    else:
        uuid_filename = str(uuid.uuid4())


    new_qrcode = pyqrcode.create(uuid_filename)

    filename = 'tmp/' + uuid_filename + '.png'

    new_qrcode.png(file=filename, scale=10)


    # Save it to the DB
    qr = QRCodes(value=uuid_filename, description="", image_location=str(filename))
    
    db.session.add(qr)
    db.session.commit()

    return send_file(filename, mimetype="image/png")


@app.route("/api/delete/<row_id>")
def remove_record(row_id):
    
    row = QRCodes.query.get(row_id)

    try:
        db.session.delete(row)
        db.session.commit()
    except (exc.IntegrityError, exc.OperationalError):
        logging.warning("Could not delete rows, rolling back")
        db.session.rollback()

    return redirect("/")



@app.route("/images/tmp/<path:filename>")
@app.route("/images/<path:filename>")
def serve_file(filename):
    return send_from_directory("tmp", filename, as_attachment=False)




@app.template_filter()
def EE_date(text, camera_id=None):
    if camera_id:
        cam = een.find_by_esn(camera_id)
        
        if cam:
            dt = een._EEN_timestamp_to_datetime(text)
            local_tz = pytz.timezone(cam.timezone)
            
            return local_tz.localize(dt).strftime('%Y-%m-%d %H:%M:%S %Z')



    dt = een._EEN_timestamp_to_datetime(text)
    return dt




if __name__ == "__main__":
    # app.secret_key = os.urandom(128)
    # replace this with your own secret
    app.secret_key = b'b\x05\x95\xfa"\xeb\xb8\xa97\xbf[\xb7\x0e\x85}\x9b=t\xb6)\xe0\x12\xd2\x8fn`\xfav\xd6\x8b\xe8\x9f\xc3t\x8bo9\xdez\xa1\xe7\xa8\xff\x8dE\x99r\xe8\x01\xb4\x9e\x9c[4\xb6\xc2jD\xef\xc9k\xe2\nQe\xf0\xfc\x99Q\xd9k\xc8fD[\x18}\xfa\x96\x02\xe8\x12h\x17\\\xd1\xeb\x1b)\x144\xa4\xde\xdf\x1c\x01\x05{\xb6\x00{\x05\x82\x9c\xed\xa7\x05~o\xe5\x05[t\xc9\x11\xdf\xb7?\x04\x80\xb0\x90\x8d\xfa\xa2j\xc0U'
    app.run(debug=False, host='0.0.0.0', port=3000)


