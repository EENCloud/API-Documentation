import json
import requests
from .settings import *
from datetime import *

import logging
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.WARN)

class Camera():
    def __init__(self, camera_id=None, name=None, bridges=None, utcOffset=None, timezone=None, camera_info=None, camera_info_status_code=None, status=None, tags = [], ip_address=None):
        self.camera_id = camera_id
        self.name = name
        self.bridges = bridges
        self.utcOffset = utcOffset
        self.timezone = timezone
        self.camera_info = camera_info
        self.camera_info_status_code = camera_info_status_code
        self.videos = []
        self.previews = [],
        self.tags = tags,
        self.ip_address = ip_address,
        self.camera_parameters = {},
        self.status = status
        self.status_text = {    'registered': False,
                                'camera_on': False,
                                'streaming': False,
                                'recording': False
                            }

        self.parse_status()
        self._clean_up_ip_address()
        # self._get_camera_parameters()

    def to_dict(self):
        self.status_text = self.parse_status()

        return {
            'camera_id': self.camera_id,
            'name': self.name,
            'bridges': self.bridges,
            'utcOffset': self.utcOffset,
            'timezone': self.timezone,
            'camera_info': self.camera_info,
            'camera_info_status_code': self.camera_info_status_code,
            'videos': self.videos,
            'previews': self.previews,
            'status': self.status,
            'status_text': self.status_text
        }

    def _clean_up_ip_address(self):
        clean_ip = self.ip_address

        if type(clean_ip) == tuple:
            clean_ip = clean_ip[0]
        
        self.ip_address = clean_ip.replace('*', '')
        return self.ip_address

    def _get_camera_parameters(self, instance=None):
        url = "%s/g/device?id=%s" % (instance.host, self.camera_id)

        res = instance.session.get(url=url)
        if res:
            if res.status_code == 200:
                if res.json():
                    self.camera_parameters = res.json()
                else:
                    logging.error("Response is not JSON")
                    return None
            else:
                logging.error( "_get_camera_parameters call returned %s" % res.status_code)
                return None
        return None

    def update_device_details(self, instance=None, body=None):
        if instance and body:
            
            url = "%s/g/device" % instance.host

            if body['id']:
                res = instance.session.post(url=url, json=body, headers={'Content-Type': 'application/json'} )

                if res:

                    if res.status_code == 200:
                        
                        return res.json()

                    else:
                        logging.error("update_device_details call failed with: %s" % res.status_code)
                else:
                    logging.error("update_device_details call failed")
                pass
            else:
                logging.error("Need to have an id in the post body")

        else:
            logging.error("Need to pass in a JSON body to post")
            return None


    def update(self):
        pass


    def parse_status(self):
        STATUS_BITMASK_ONLINE           = 0x100000
        STATUS_BITMASK_ON               = 0x020000
        STATUS_BITMASK_CAMERA_STREAMING = 0x040000
        STATUS_BITMASK_VIDEO_RECORDING  = 0x080000

        ret = self.status_text

        ret['registered'] = bool(self.status & STATUS_BITMASK_ONLINE)
        ret['camera_on'] = bool(self.status & STATUS_BITMASK_ON)
        ret['streaming'] = bool(self.status & STATUS_BITMASK_CAMERA_STREAMING)
        ret['recording'] = bool(self.status & STATUS_BITMASK_VIDEO_RECORDING)

        return ret
 



    def create_annotation(self, instance=None, timestamp='now', ns=None, obj={}):
        if ns:
            
            url = "%s/annt/set?id=%s&ts=%s&ns=%s" % (instance.host, self.camera_id, timestamp, ns)
            obj['id'] = self.camera_id

            res = instance.session.put(url=url, json=obj, headers={'Content-Type': 'application/json'} )
            
            if res.status_code:

                if res.status_code == 200:
                    
                    return res.json()

                else:
                    logging.error("create_annotation call failed with: %s" % res.status_code)
            else:
                logging.error("create_annotation call didn't return a status_code")

        else:
            logging.error("Need to pass in a namespace")
            return None

    def update_annotation(self, instance=None, timestamp='now', ns=None, obj={}, annt_type='mod', uuid=''):
        if ns:
            
            url = "%s/annt/set?u=%s&id=%s&ts=%s&ns=%s&type=%s"  % (instance.host, uuid, self.camera_id, timestamp, ns, annt_type)
            obj['id'] = self.camera_id

            res = instance.session.post(url=url, json=obj, headers={'Content-Type': 'application/json'} )
            
            if res.status_code:

                if res.status_code == 200:
                    
                    return res.json()

                else:
                    logging.error("update_annotation call failed with: %s" % res.status_code)
            else:
                logging.error("update_annotation call didn't return a status_code")

        else:
            logging.error("Need to pass in a namespace")
            return None







class EagleEye():

    def __init__(self):
        self.host = "https://login.eagleeyenetworks.com"
        self.session = requests.Session()
        self.headers = { 'Authorization': settings.api_key }
        self.cameras = []
        self.bridges = []
        self.switches = []
        self.user = None
        self.users = []
        self.auth_key = None

    def to_dict(self):
        return {
            'host': self.host,
            'cameras': self.cameras,
            'bridges': self.bridges,
            'switches': self.switches,
            'user': self.user,
            'users': self.users,
            'auth_key': self.auth_key
        }

    def check_cookie(self):
        def wrapper(*args, **kwargs):
            """ decorator to check if the current cookie is still valid """
            url = self.host + "/g/aaa/isauth"
            res = session.get(url, headers=self.headers, data={})

            if res and res.status_code == 200:
                return wrapper
        
            elif res or res.status_code == 401:
                logging.warn("cookie is no longer valid, need to login again")

    def find_by_esn(self, target_esn):
        ret =  [i for i in self.cameras if i.camera_id == target_esn]
        if len(ret) > 0:
            return ret[0]
        else:
            return None


    def find_by_ip(self, ip_address):
        ret =  [i for i in self.cameras if i.ip_address == ip_address]
        if len(ret) > 0:
            return ret[0]
        else:
            return None

    def _update_devices(self):
        """ Gets the list of device ids, filter into correct bucket """
        url = self.host + "/g/device/list"
        res = self.session.get(url=url, headers=self.headers)

        if res and res.status_code == 200:
            self.cameras = [i[1] for i in res.json() if i[3] == 'camera']
            self.bridges = [i[1] for i in res.json() if i[3] == 'bridge']
            self.switches = [i[1] for i in res.json() if i[3] == 'switches']

            self.cameras = []
            for device in [i for i in res.json() if i[3] == 'camera']:
                c = Camera(
                        camera_id = device[1],
                        name = device[2],
                        bridges = device[4],
                        utcOffset = device[12],
                        timezone = device[11],
                        status = device[10],
                        ip_address = device[14],
                        tags = device[7]
                    )
                self.cameras.append(c)

        return True


    def get_user_id_by_email(self, email=None):
        if email:
            results = [i for i in self.users if i[3] == email]
            if len(results) > 0:
                return results[0][0]
        return None


    def _datetime_to_EEN_timestamp(self, in_time):
        """
            Takes a normal datetime object and returns it in EEN format
        """
        pattern = "%Y%m%d%H%M%S.%f"
        return in_time.strftime(pattern)[:-3]

    def _EEN_timestamp_to_datetime(self, een_time):
        """
            Take a EEN timestamp string and returns a datetime object
        """
        pattern = "%Y%m%d%H%M%S.%f"
        return datetime.strptime(een_time, pattern)

    def login(self, username=None, password=None):
        """ 
            Goes through the two step login process.  
            On success it sets the cookie in self.cookie and returns the user object 
        """
        if username and password:
            payload = {
                "username": username,
                "password": password
            }
            url = self.host + "/g/aaa/authenticate"
            res = self.session.post(url=url, headers=self.headers, data=payload)

            if res and res.status_code == 200:
                logging.info("login(step 1): %s" % res.status_code)
                token = res.json()['token']
                payload = { 'token': token }
                url = self.host + "/g/aaa/authorize"

                res = self.session.post(url=url, headers=self.headers, data=payload)

                if res and res.status_code == 200:
                    logging.info("login(step 2): %s" % res.status_code)

                    if self._update_devices():
                        logging.info("     - successfully updated devices")
                    else:
                        logging.info("     - failed to update devices")

                    self.user = res.json()
                    self.host = "https://%s.eagleeyenetworks.com" % self.user['active_brand_subdomain']
                    
                    if 'auth_key' in self.session.cookies:
                        self.auth_key = self.session.cookies['auth_key']

                    return True

                else:
                    logging.error("Login (step2) failed: %s" % res.status_code)
                    return False
            else:
                logging.error("Login (step1) failed: %s" % res.status_code)
                return False
        else:
            logging.error("Login needs to be called with a username and password")
            return False


    def _format_url_for_download(self, esn=None, start_time=None, end_time=None, video_format='MP4'):
        """
            Returns the URL for downloading the video clip as an MP4.
        """
        if esn and start_time and end_time:
            return "%s/asset/play/video.%s?id=%s&start_timestamp=%s&end_timestamp=%s" % (self.host, video_format, esn, start_time, end_time)
        else:
            logging.error("format_url_for_download needs esn, start_time and end_time")








