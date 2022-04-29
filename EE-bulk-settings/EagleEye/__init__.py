import json
import requests
from .settings import *
from datetime import *

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
        url = f"{instance.host}/g/device?id={self.camera_id}"

        res = instance.session.get(url=url)
        if res:
            if res.status_code == 200:
                if res.json():
                    self.camera_parameters = res.json()
                else:
                    print("Response is not JSON")
                    return None
            else:
                print( f"_get_camera_parameters call returned {res.status_code}")
                return None
        return None

    def update_device_details(self, instance=None, body=None):
        if instance and body:
            
            url = f"{instance.host}/g/device"
            # print(url)

            # print(json.dumps(body))
            if body['id']:
                res = instance.session.post(url=url, json=body, headers={'Content-Type': 'application/json'} )

                if res:
                    # print(res)
                    if res.status_code == 200:
                        
                        return res.json()

                    else:
                        print(f"update_device_details call failed with: {res.status_code}")
                else:
                    print("update_device_details call failed")
                pass
            else:
                print("Need to have an id in the post body")

        else:
            print("Need to pass in a JSON body to post")
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
 


    def get_preview_list(self, instance=None, start_timestamp=None, end_timestamp=None, asset_class="all", count=None):
        if instance:
            if start_timestamp and end_timestamp:
                url = f"{instance.host}/asset/list/image?id={self.camera_id}&start_timestamp={start_timestamp}&end_timestamp={end_timestamp}&asset_class={asset_class}"
            elif start_timestamp and count:
                url = f"{instance.host}/asset/list/image?id={self.camera_id}&start_timestamp={start_timestamp}&count={count}&asset_class={asset_class}"
            elif start_timestamp:
                url = f"{instance.host}/asset/list/image?id={self.camera_id}&start_timestamp={start_timestamp}&asset_class={asset_class}"
            else:
                print('get_preview_list needs start_timestamp, and end_timestamp or count')
                return False

            res = instance.session.get(url=url)
            if res:
                if res.status_code == 200:
                    for item in res.json():
                        self.previews.append( (item['s']) )
                    
                    self.previews = list(set(sorted(self.previews)))
                    return self.previews
                else:
                    print(f"get_preview_list call failed with: {res.status_code}")
            else:
                print("get_preview_list call failed")
        else:
            print("need to pass in an instance of EagleEye")


    def download_image(self, instance=None, timestamp=None, modifier="asset", asset_class="all"):
        if instance:
            if timestamp:
                url = f"{instance.host}/asset/{modifier}/image.jpeg?id={self.camera_id}&timestamp={timestamp}&asset_class={asset_class}"
                # print(url)
                res = instance.session.get(url=url)

                if res.status_code == 200:
                    return res.content
                else:
                    print(f"download_image returned {res.status_code}")
            else:
                print('downlaod_image needs a timestamp or now')
        else:
            print('need to pass in an instance of EagleEye')

        return None


    def get_video_list(self, instance= None, start_timestamp=None, end_timestamp=None, count=None, options='coalesce'):
        if instance:
            if start_timestamp and end_timestamp:
                url = f"{instance.host}/asset/list/video?id={self.camera_id}&start_timestamp={start_timestamp}&end_timestamp={end_timestamp}&options={options}"
            elif start_timestamp:
                url = f"{instance.host}/asset/list/video?id={self.camera_id}&start_timestamp={start_timestamp}&count={count}&options={options}"
            else:
                    print('get_view_list needs start_timestamp, and end_timestamp or count')
                    return False

            res = instance.session.get(url=url)
            if res:
                if res.status_code == 200:
                    for item in res.json():
                        self.videos.append( (item['s'], item['e']) )

                    self.videos = list(set(sorted(self.videos)))
                    return self.videos

                else:
                    print(f"get_video_list call failed with: {res.status_code}")
            else:
                print("get_video_list call failed")
        else:
                print("need to pass in an instance of EagleEye")


    def __repr__(self):
        return f"{self.camera_id} - {self.name}"


    def _format_url_for_download(self, start_time=None, end_time=None, video_format='MP4'):
        """
            Returns the URL for downloading the video clip as an MP4.
        """
        if esn and start_time and end_time:
            return "%s/asset/play/video.%s?id=%s&start_timestamp=%s&end_timestamp=%s" % (self.host, video_format, self.camera_id, start_time, end_time)
        else:
            print("WARNING: format_url_for_download needs start_time and end_time")



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
                        timezone = device[11],
                        status = device[10],
                        ip_address = device[14],
                        tags = device[7]
                    )
                self.cameras.append(c)

        return True

    def get_user_list(self):

        url = f"{self.host}/g/user/list"
        res = self.session.get(url=url)

        if res:
            if res.status_code == 200:
                for item in res.json():
                    self.users.append(item)

                self.users = sorted(self.users)
            else:
                print(f"get_users_list call failed with: {res.status_code}")
        else:
            print("get_users_list call failed")


    def get_user_id_by_email(self, email=None):
        if email:
            results = [i for i in self.users if i[3] == email]
            if len(results) > 0:
                return results[0][0]
        return None


    def get_user_details(self, user_id=None):
        if user_id:
            
            url = f"{self.host}/g/user?id={user_id}"
            res = self.session.get(url=url)

            if res:
                if res.status_code == 200:
                    
                    return res.json()

                else:
                    print(f"get_users_details call failed with: {res.status_code}")
            else:
                print("get_users_details call failed")

        else:
            print("Need to pass in a user_id")
            return None


    def update_user_details(self, user=None):
        if user:
            
            url = f"{self.host}/g/user"
            print(url)
            print(user)
            print(json.dumps(user))
            res = self.session.post(url=url, json=user, headers={'Content-Type': 'application/json'} )

            if res:
                print(res)
                if res.status_code == 200:
                    
                    return res.json()

                else:
                    print(f"update_users_details call failed with: {res.status_code}")
            else:
                print("update_users_details call failed")

        else:
            print("Need to pass in a user_id")
            return None


    




    def _datetime_to_EEN_timestamp(in_time):
        """
            Takes a normal datetime object and returns it in EEN format
        """
        pattern = "%Y%m%d%H%M%S.%f"
        return in_time.strftime(pattern)[:-3]

    def _EEN_timestamp_to_datetime(een_time):
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








