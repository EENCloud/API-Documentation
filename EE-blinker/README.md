## EE-blinker for Eagle Eye Networks Poll Stream ##

This is a Node.js client that follows the [Eagle Eye Networks API](https://apidocs.eagleeyenetworks.com/apidocs/).  It listens for new motion events and then toggles an LED.  This is the basis for our real-time feed.

## Lifecycle of the app ##
The following steps need to be performed in order, but any call can be made once user is logged-in.

 - Login (step 1)
 - Login (step 2)
 - Current user's information is returned by Login (step 2)
 - Get device list
 - Subscribe to poll stream
 - Get subsequent events from poll stream

### Installation ###

 - install [Node.js](http://nodejs.org)
 - run `npm install	` 
 - run `npm start	`
 - go to [http://localhost:3000](http://localhost:3000)

### Extras ###
Checkout out the facedetection branch if you want to try something different with the previews.  It will show the image in grayscale if it doesn't detect a face.  Not really useful, but interesting example of using node-opencv

### Configure ###

 Edit `config.js` and replace 'your_username', 'your_password', and 'your_api_key' with your username, password, and api key.


        module.exports = {
            // credentials for the app to use
            'username': 'your_username',
            'password': 'your_password',
            'api_key': 'your_api_key',

            // if you only want a subset of the cameras, put the ESNs here,
            // empty means show all
            'filter_cameras': [
                "camera_esn"
            ],

            // what serial port should be connect to
            'serial_port': '/dev/cu.usbmodem14101',

            // where to save the auth file
            'path_to_saved_cookie': './cookie'


        }



