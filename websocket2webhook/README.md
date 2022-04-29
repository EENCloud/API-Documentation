## Websocket to Webhook ##

### Introduction ###
This is an example of subscribing to the [Eagle Eye Video API](https://een.com) in order to monitor status of cameras and bridges.  This example uses [websocket polling](https://apidocs.eagleeyenetworks.com/apidocs/#websocket-polling).  It will look for events the user cares about and store them inside of a queue.  The workers pull items off the queue and send them as webhooks.

### Requirements ###
This example is written in Node.js and uses Redis but there is nothing special about this combination and could be replicated in another technology.

### Installation ###
- clone this repo
- run `npm install`
- create `config.js` with your credentials
- edit `worker.js` with any additional programming

### Configuration ###
You will need to add valid Eagle Eye crendentials in order to use this.  Please add them into `config.js`.  An example version of it is included below for reference.

```

module.exports = {

        // credentials for the app to use
        'username': <email>,
        'password': <password>,
        'api_key': <api_key>,

        // where to save the auth file
        'cookie_path': './cookie.json',

        // port for the Kue UI
        'port': 3000,

        // how many workers should we spawn
        'number_of_workers': 1,

        // what events should we listen for
        'listen_for_recordings': false,
        'listen_for_camera_on': true,
        'listen_for_streaming': true,
        'listen_for_registered': true,

        // turn on and off specific logging
        'debug': false,
        'info': true,

        // should completed items be removed from the UI?
        'remove_on_complete': false,
        
        'webhook_url': <url to call>,

        'redis_options': {
            prefix: 'q',
            redis: {
                port: 6379,
                host: 'db', // probably 127.0.0.1 or db if you're using Docker
                auth: '',
                options: {
                    // see https://github.com/mranney/node_redis#rediscreateclient
                }
            }
        }

    }


```

### Customization ###
The primary area to add your own customizations is in `worker.js`.  The `doSomething` hook that runs on every item enqueued.  It is very important that you call `done()` when you are finished processesing each item.

There are hooks provided for all the queue events (complete, failed, failed attempt, progress).  You can add your own logic to if you want to be notified of failed webhooks or if you want to keep additional logging.


### Webhook ###
The point of this is to monitor the poll stream looking for matching events and then call a user provided URL.  The code makes a HTTP POST request with a JSON object in the body.

Example JSON payload:

```
{
	'device': '10067f22', 
	'status': 1441855, 
	'invalid': False, 
	'camera_on': True, 
	'streaming': True, 
	'recording': False, 
	'registered': True, 
	'title': '10067f22 has stopped recording'
}
```

The following table includes details on the returned values.


| Key        | Description           |
| ------------- |:------------- |
| Device      | This is the Eagle Eye device ID (ESN) |
| Status  | This is the Status Bitmask |
| Invalide | If the Status Bitmask is invalid this will be true and the update can be ignored|
| Camera On | The user has turned the camera on or off.  The device is still connected but not recording because of a user action |
| Streaming | Bridge is getting data from the Camera |
| Recording | Camera is currently recording |
| Registered | Device has a connection to the Eagle Eye cloud |
| Title | Text that describes the event and is displayed in the Kue UI |


### Notes for Developers ###
Make sure that you run `git update-index --skip-worktree config.js` so that git doesn't track changes to your config.js file.


### Docker Notes ###
Who really knows how any of this stuff works.  Just run `docker-compose up` and see what happens.  It worked once, but that might have just been a fluke.
