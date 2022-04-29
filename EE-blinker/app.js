var r           =       require('request'),
    u           =       require('underscore')._,
    router      =       require('router'),
    repl        =       require('repl');

var route       =       router();

var app         =       require('http').createServer(route),
    io          =       require('socket.io').listen(app, { log: false }),
    fs          =       require('fs');

    app.listen(3000);


var  out        =       console.log,
     config     =       require('./config'),
     host       =       'https://login.eagleeyenetworks.com';

var user        =       {},
    devices     =       {
                            cameras: [],
                            bridges: []
                        },
    last_img    =       {};
    cached_img  =       {};

const SerialPort = require('serialport');
const Readline = require('@serialport/parser-readline');
const port = new SerialPort(config.serial_port, { baudRate: 9600 });

var reason_LED_is_on = undefined;

var debug = function(arg) {
    repl.start({
      prompt: "node via stdin> ",
      input: process.stdin,
      output: process.stdout
    }).context.arg = arg;
};

var cookie_jars = r.jar();

function startUp(success, failure) {
    out('**********************************');
    out('           Starting up            ');
    out('**********************************');
    if ( typeof success === 'function') success(); // call success callback   
}

function login(success, failure) {
    r.get({
            url: host + '/g/aaa/isauth',
            jar: cookie_jars,
            headers: {'Authorization': config.api_key }
        }, function(err, res, body) {
            if (err) { 
                out("error in pre-login");
                out(err.stack);
                if ( typeof failure === 'function') failure(); 
            }
            if (!err) {
                console.log('isauth status code: ' + res.statusCode);
                switch(res.statusCode) {
                    case 200:
                        out('*********** Auth is still good ***************');
                        if ( typeof success === 'function') success();
                        break;
                    default:
                        r.post({
                            url: host + '/g/aaa/authenticate',
                            json: true,
                            body: { 'username': config.username, 'password': config.password, 'realm': 'eagleeyenetworks' },
                            headers: {'Authorization': config.api_key }
                            }, function(err, res, body) {
                                if (err) { out("error in login1"); out(err.stack); }
                                if (!err) {
                                    switch(res.statusCode) {
                                        case 200:
                                            r.post({ url: host + '/g/aaa/authorize',
                                                    jar: cookie_jars,
                                                    json: true, 
                                                    body: { token: res.body.token },
                                                    headers: {'Authorization': config.api_key }
                                                }, function(err, res, body) {
                                               if (err) { out("error in login2"); out(err.stack); }
                                               if (!err && res.statusCode == 200) {
                                                    out('**********************************');
                                                    out('           Logged in              ');
                                                    out('**********************************');
                                                    user = res.body;
                                                    if ( typeof success === 'function') success(); // call success callback
                                                }
                                            })
                                            break;
                                        default:
                                            out(res.statusCode + ': ' +  res.body);
                                            if ( typeof failure === 'function') failure(); // call failure callback

                                    }
                                }
                    })

                }

            }
    })
}

function getDevices(success, failure) {
    r.get({ url: host + '/g/list/devices',
            json: true,
            jar: cookie_jars,
            headers: {'Authorization': config.api_key }
        }, function(err, res, body) {
        if (err) { out("error in getDevices"); out(err.stack);  bootstrap(); }
        if (!err && res.statusCode == 200) {
            out('**********************************');
            out('           Grabbed Devices        ');
            out('**********************************');

            u.each(res.body, function(device) {
                var tmp = {};
                if(device[3] === 'camera') {
                    tmp = {
                        deviceID:           device[1] || '',
                        deviceStatus:       device[5] || ''
                    };
                    devices.cameras.push(tmp);
                } else {
                    tmp = {
                        deviceID:           device[1] || '',
                        deviceStatus:       device[5] || ''
                    };
                    devices.bridges.push(tmp);
                }
            });

            if ( typeof success === 'function') success(); // call success callback
        } else {
            out("Error in getDevices, got: ", res.statusCode);
            bootstrap();
        }
    });
}

function startPolling() {
    var obj = { 'cameras': {} };

    // u.each(u.filter(devices.bridges, function(item) { return item.deviceStatus === 'ATTD'; } ), function(item) {
    //     obj.cameras[item.deviceID] = { "resource": [] };
    // });

    var cameras_to_poll = devices.cameras

    if(config.filter_cameras.length > 0) {
        cameras_to_poll = u.filter(devices.cameras, function(item) { return config.filter_cameras.indexOf(item.deviceID) > -1 })
    }

    u.each(u.filter(cameras_to_poll, function(item) { return item.deviceStatus === 'ATTD' } ), function(item) {
        //obj.cameras[item.deviceID] = { "resource": ["event"], "event": ["ROMS", "ROME"] };
        obj.cameras[item.deviceID] = { "resource": ["event", "preview"], "event": ["ROMS", "ROME"] };
    });

    out('**********************************');
    out('           Start Polling          ');
    out('**********************************');

    process.stdout.write("Making a request from startPolling... ");
    r.post({
            url:    host + '/poll',
            jar: cookie_jars,
            time: true,
            body:   JSON.stringify( obj),
            headers: {'Authorization': config.api_key }
           }, function(err, res, body) {
                if (err) { out("error in startPolling"); out(err.stack); startPolling() };
                if (!err) {
                    console.log(res.statusCode + " in " + res.elapsedTime + 'ms');
                    switch(res.statusCode) {
                        case 200:
                            keepPolling();
                            break;
                        case 400:
                            out(' *********** 400 Bad Request ??? *************');
                            out(res.headers);
                            out(res.body);
                            out(cookie_jars);
                            out(obj)
                            startPolling();
                            break;
                        case 500:
                            out(res.statusCode + ' in keepPolling()');
                            out(res.headers);
                            out(res.body);
                            startPolling();
                            break;
                        case 502:
                            out(' *********** 502 Gateway timeout *************');
                            keepPolling();
                            break;
                        case 401:
                            handle_401();
                            break;
                         default:
                            out(res.statusCode);
                            out(res.headers);
                            out(res.body);
                            out('**********************************');
                            out('           Restart Polling        ');
                            out('**********************************');
                            startPolling();
                            break;
                    }
                }

    });


}

function keepPolling() {
    //out('**********************************');
    //out('           Keep Polling           ');
    //out('**********************************');

    process.stdout.write("Making a request from keepPolling... ");
    r.get({
            url:    host + '/poll',
            jar: cookie_jars,
            json: true,
            time: true,
            headers: {'Authorization': config.api_key }
           }, function(err, res, body) {
                if(res && res.statusCode) {
                    console.log(res.statusCode + " in " + res.elapsedTime + 'ms');
                }
                if (err) { out("error in keepPolling"); out(err.stack); keepPolling();};
                if (!err) {
                    switch(res.statusCode) {
                        case 200:
                            // got a valid polling cookie
                            processPollingData(res.body);
                            keepPolling();
                            break;
                        case 400:
                            out(' *********** 400 Bad Request ??? *************');
                            out(res.headers);
                            out(res.body);
                            out(cookie_jars);
                            startPolling();
                            break;
                        case 401:
                            handle_401();
                            break;
                        case 500:
                            out(res.statusCode + ' in keepPolling()');
                            out(res.headers);
                            out(res.body);
                            startPolling();
                            break;
                        case 502:
                            out(' *********** 502 Gateway timeout *************');
                            //startPolling();
                            keepPolling();
                            break;
                        default:
                            out(res.statusCode + ' in keepPolling()');
                            out(res.headers);
                            out(res.body);
                            out('**********************************');
                            out('           Restart Polling        ');
                            out('**********************************');
                            startPolling();
                            break;
                    }
                }

    });

}

function processPollingData(data) {
    //out('**********************************');
    //out('           Processing Data        ');
    //out('**********************************');
    //out(data);

    // console.log(data);
    // console.log(data['cameras']);

    if(data.cameras['100a54ec'].event['ROMS']) {

        if(reason_LED_is_on == undefined) {
            port.write('1\n');
            console.log("Turning ON: " + data.cameras['100a54ec'].event['ROMS'].eventid)
            reason_LED_is_on = data.cameras['100a54ec'].event['ROMS'].eventid 
        } else {
            console.log("Got an ON when it was already ON")
        }
    }

    if(data.cameras['100a54ec'].event['ROME']) {
        if(reason_LED_is_on) {
            port.write('2\n');
            console.log("Turning OFF: " + data.cameras['100a54ec'].event['ROME'].eventid);  
        } else {
            console.log("Got an OFF without a corresponding ON")
        }
        
        reason_LED_is_on = undefined
    }

}

function handle_401() {
    out("Got a 401, going to start the bootstrap process over again")
    bootstrap();
}


function bootstrap() {
    
    startUp( function() {
        login( function() {
            getDevices( function() {
                startPolling()
            },
            function() {
                console.log('Failure case for getDevices()');
                bootstrap();
            });
        },
        // failure case for login
        function() {
            console.log('Failed to login using these credentials  ' + config.username + ' : ' + config.password );
        });
    });
}


app.on('error', function(e) {
    console.log(e)
});



process.on('uncaughtException', function(err) {
  console.log('Caught exception: ' + err);
  switch(err) {
    case 'Error: Parse Error':
        out(err);
        bootstrap();
        break;
    default:
        out('We caught an uncaughtException')
        out(err);
        bootstrap();
        break;
  }
});

process.on('SIGTERM', function () {
  server.close(function () {
    process.exit(0);
  });
});

bootstrap();
