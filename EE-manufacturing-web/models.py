

from flask_sqlalchemy import SQLAlchemy

from settings import *


db = SQLAlchemy()



__all__ = ['db', 'QRCodes', 'Annotations', 'Credentials', 'Cameras']




class QRCodes(db.Model):
    id                      = db.Column(db.Integer, primary_key=True)
    value                   = db.Column(db.String(64), nullable=True)
    description             = db.Column(db.String(128), nullable=True)
    image_location          = db.Column(db.String(128), nullable=True)
    annotations             = db.relationship('Annotations', backref='qrcodes', lazy=True)


    def __repr__(self):
        return '<QRCodes %s - %s>' % (self.id, self.value)

    def to_dict(self):
        return {
            'id': self.id,
            'value': self.value,
            'description': self.description,
            'image_location': self.image_location,
            'annotations': self.annotations
        }



class Annotations(db.Model):
    id                      = db.Column(db.Integer, primary_key=True)
    camera_id               = db.Column(db.String(8), nullable=True)
    EE_starttime            = db.Column(db.String(18), nullable=True)
    EE_endtime              = db.Column(db.String(18), nullable=True)
    EE_uuid                 = db.Column(db.String(64), nullable=True)
    qrcode_id               = db.Column(db.Integer, db.ForeignKey(QRCodes.id), nullable=True)


    def __repr__(self):
        return '<Annotations %s:%s-%s>' % (self.camera_id, self.EE_starttime, self.EE_endtime)

    def to_dict(self):
        return {
            'id': self.id,
            'camera_id': self.id,
            'EE_starttime': self.EE_starttime,
            'EE_endtime': self.EE_endtime,
            'EE_UUID': self.EE_uuid
        }


class Credentials(db.Model):
    id                      = db.Column(db.Integer, primary_key=True)
    account_id              = db.Column(db.String(10), nullable=True)
    username                = db.Column(db.String(255), nullable=False)
    password                = db.Column(db.String(255), nullable=False)
    auth_key                = db.Column(db.String(255), nullable=True)
    cameras                 = db.relationship('Cameras', backref='cameras', lazy=True)


    def __repr__(self):
        return '<Credentials %s>' % (self.username)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'password': self.password,
            'account_id': self.account_id
        }



class Cameras(db.Model):
    id                      = db.Column(db.Integer, primary_key=True)
    camera_id               = db.Column(db.String(8), nullable=False)
    camera_name             = db.Column(db.String(100), nullable=True)
    account_id              = db.Column(db.Integer,  db.ForeignKey('credentials.id'), nullable=False)
    last_EE_update          = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return '<Cameras %s [%s]>' % (self.camera_name, self.camera_id)

    def to_dict(self):
        return {
            'id': self.id,
            'camera_id': self.camera_id,
            'camera_name': self.camera_name,
            'account_id': self.account_id,
            'last_EE_update': self.last_EE_update
        }









