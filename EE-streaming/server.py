
import local_settings

from EagleEye import EagleEye
een = EagleEye()

from twisted.web import server, resource
from twisted.internet import reactor, endpoints, task

import json


output = { 
            "cameras": None,
            "auth_key": None,
            "account": None,
            "active_brand_subdomain": None
        }


class Counter(resource.Resource):
    isLeaf = True

    def render_GET(self, request):
        request.setHeader(b"content-type", b"application/json")
        request.setHeader('Access-Control-Allow-Origin', '*')
        request.setHeader('Access-Control-Allow-Methods', 'GET')
        request.setHeader('Access-Control-Allow-Headers', 'x-prototype-version,x-requested-with')
        request.setHeader('Access-Control-Max-Age', '2520') # 42 hours
        
        content = json.dumps(output)
        return content.encode("ascii")



def login_to_EagleEye(een):
    print("login_to_EagleEye called")
    login = een.login(local_settings.username, local_settings.password)
    if login:
        print(f"login succeeded, updating devices and cookie {een.session.cookies['auth_key']}")
        output['auth_key'] = een.session.cookies['auth_key']
        output['account'] = een.user['active_account_id']
        output['active_brand_subdomain'] = een.user['active_brand_subdomain']
        #output['cameras'] = [{"id": i.camera_id, "name": i.name} for i in een.cameras] 
        # filtering out the Koi pond camera because it doesn't have the bandwidth to live stream
        output['cameras'] = [{"id": i.camera_id, "name": i.name} for i in een.cameras if i.camera_id != '100f3e82'] 
    else:
        print("login_to_EagleEye failed")



def check_cookie():
    #check if auth_key is valid
    if output['auth_key']:
        try:
            response = een.session.request("GET", "https://login.eagleeyenetworks.com/g/aaa/isauth")
            if response.status_code == 200:
                print(f"cookie is still good {een.session.cookies['auth_key']}")
                output['auth_key'] = een.session.cookies['auth_key']
            else:
                print(f"isauth check failed with {response.status_code}")
                login_to_EagleEye(een)

        except ConnectionError as e:
            print(f"failed on call to check auth_key, logging-in again")
            login_to_EagleEye(een)
            
    else:
        print(f"auth_key is set to {output['auth_key']}")
        login_to_EagleEye(een)




l = task.LoopingCall(check_cookie)
l.start(30)

endpoints.serverFromString(reactor, "tcp:3002").listen(server.Site(Counter()))
reactor.run()
