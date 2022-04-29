import json
import requests
from .settings import *

from datetime import datetime

class Camera():
    def __init__(self, camera_id=None, name=None, bridges=None, utcOffset=None, timezone=None, camera_info=None, camera_info_status_code=None):
        self.camera_id = camera_id
        self.name = name
        self.bridges = bridges
        self.utcOffset = utcOffset
        self.timezone = timezone
        self.camera_info = camera_info
        self.camera_info_status_code = camera_info_status_code
        self.videos = []
        self.previews = []

    def to_dict(self):
        return {
            'camera_id': self.camera_id,
            'name': self.name,
            'bridges': self.bridges,
            'utcOffset': self.utcOffset,
            'timezone': self.timezone,
            'camera_info': self.camera_info,
            'camera_info_status_code': self.camera_info_status_code,
            'videos': set(self.videos),
            'previews': self.previews
        }

    def update(self):
        pass

    def get_preview_list(self, camera_id=None, start_timestamp=None, end_timestamp=None, asset_class="all"):
        if end_timestamp:
            url = f"{instance.host}/asset/list/image?id={self.camera_id}&start_timestamp={start_timestamp}&end_timestamp={end_timestamp}&asset_class={asset_class}"
        else:
            url = f"{instance.host}/asset/list/image?id={self.camera_id}&start_timestamp={start_timestamp}&count={count}&asset_class={asset_class}"

        res = instance.session.get(url=url)

        if res:

            if res.status_code == 200:

                for item in res.json():
                    self.previews.append( (item['s'], item['e']) )

                    self.previews = sorted(self.previews)
            else:
                print(f"get_preview_list call failed with: {res.status_code}")
        else:
            print("get_preview_list call failed")


    def get_video_list(self, instance= None, start_timestamp=None, end_timestamp=None, count=None, options='coalesce'):

        if end_timestamp:
            url = f"{instance.host}/asset/list/video?id={self.camera_id}&start_timestamp={start_timestamp}&end_timestamp={end_timestamp}&options={options}"
        else:
            url = f"{instance.host}/asset/list/video?id={self.camera_id}&start_timestamp={start_timestamp}&count={count}&options={options}"

        res = instance.session.get(url=url)

        if res:

            if res.status_code == 200:

                for item in res.json():
                    self.videos.append( (item['s'], item['e']) )

                self.videos = sorted(list(set(self.videos)))

            else:
                print(f"get_video_list call failed with: {res.status_code}")
        else:
            print(f"get_video_list call failed: {res.status_code} {url}")


    def prefetch_video(self, instance= None, start_timestamp=None, end_timestamp=None, success_hook=None, failure_hook=None):

        url = f"{instance.host}/asset/cloud/video.flv?id={self.camera_id}&start_timestamp={start_timestamp}&end_timestamp={end_timestamp}&success_hook={success_hook}&failure_hook={failure_hook}"
        
        res = instance.session.get(url=url)

        if res:

            if res.status_code == 201:
                return res.json()['data']['uuid']

            else:
                print(f"get_video_list call failed with: {res.status_code}")
        else:
            print("get_video_list call failed")


    def __repr__(self):
        return f"{self.camera_id} - {self.name}"



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

    def to_dict(self):
        return {
            'host': self.host,
            'cameras': self.cameras,
            'bridges': self.bridges,
            'switches': self.switches,
            'user': self.user,
            'users': self.users
        }

    def check_cookie(self):
        def wrapper(*args, **kwargs):
            """ decorator to check if the current cookie is still valid """
            url = self.host + "/g/aaa/isauth"
            res = session.get(url, headers=self.headers, data={})

            if res and res.status_code == 200:
                return wrapper
        
            elif res or res.status_code == 401:
                print("WARNING: Cookie is no longer valid, need to login again")

    def find_by_esn(self, target_esn):
        ret =  [i for i in self.cameras if i.camera_id == target_esn]
        if len(ret) > 0:
            return ret[0]

    def _update_devices(self):
        """ Gets the list of device ids, filter into correct bucket """
        url = self.host + "/g/device/list"
        res = self.session.get(url=url, headers=self.headers)

        if res and res.status_code == 200:
            #self.cameras = [i[1] for i in res.json() if i[3] == 'camera']
            self.bridges = [i[1] for i in res.json() if i[3] == 'bridge']
            self.switches = [i[1] for i in res.json() if i[3] == 'switches']

            self.cameras = []
            for device in [i for i in res.json() if i[3] == 'camera']:
                c = Camera(
                        camera_id = device[1],
                        name = device[2],
                        bridges = device[4],
                        utcOffset = device[12],
                        timezone = device[11]
                    )
                self.cameras.append(c)

        return True

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
                print("login(step 1): %s" % res.status_code)
                token = res.json()['token']
                payload = { 'token': token }
                url = self.host + "/g/aaa/authorize"

                res = self.session.post(url=url, headers=self.headers, data=payload)

                if res and res.status_code == 200:
                    print("login(step 2): %s" % res.status_code)

                    if self._update_devices():
                        print("     - successfully updated devices")
                    else:
                        print("     - failed to update devices")

                    self.user = res.json()
                    self.host = f"https://{self.user['active_brand_subdomain']}.eagleeyenetworks.com"
                    return True

                else:
                    print("Login (step2) failed: %s" % res.status_code)
                    return False
            else:
                print("Login (step1) failed: %s" % res.status_code)
                return False
        else:
            print("Login needs to be called with a username and password")
            return False


    def _format_url_for_download(self, esn=None, start_time=None, end_time=None, video_format='MP4'):
        """
            Returns the URL for downloading the video clip as an MP4.
        """
        if esn and start_time and end_time:
            return "%s/asset/play/video.%s?id=%s&start_timestamp=%s&end_timestamp=%s" % (self.host, video_format, esn, start_time, end_time)
        else:
            print("WARNING: format_url_for_download needs esn, start_time and end_time")








