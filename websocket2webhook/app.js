
// import npm modules
var r           =       require('request'),
    u           =       require('underscore')._,
    kue         =       require('kue'),
    ws          =       require('ws'),
    express     =       require('express');

// import local modules
var config     =       require('./config'),
    een        =       require('./een'),
    worker     =       require('./worker');

// misc items
var curr_user   =       {},
    users       =       {},
    devices     =       [],
    deviceStatus =      {},
    cameras     =       [],
    bridges     =       [];

var queue       =       kue.createQueue(config.redis_options);


/*****************
*** Helper Logging functions
*****************/

var debug = function() {
    if(config.debug) {
        console.log.apply(console, arguments);
    }
};
 
 var info = function() {
    if(config.info) {
        console.log.apply(console, arguments);
    }
 };


/*****************
*** Startup process
*****************/


var startup_items = [
    function() { een.login({'username': config.username, 'password': config.password}, postLogin, failure); },
    function() { een.getDeviceList({}, postGetDevices, failure); },
    function() { buildPollQuery(); }
];


function executeNextStep() {
    if(startup_items.length > 0)  { 
        startup_items.shift()();
    } else {
        // executeNextStep ran out of startup_items items
    }
}


/********************
*** Setting up kue
********************/


function createNewJob(type, opts) {
    var job = queue.create(type, opts).ttl(10000).save( function(err) {
        if ( err ) { debug("Error creating job ", err); }
        if ( !err ) {
            debug("Successfully create job: " + job.id);
        }
    })


    job.on('complete', function(result){
        debug('Job completed with data ', result);
        worker.onComplete(job, result);

    }).on('failed attempt', function(errorMessage, doneAttempts){
        debug('Job failed attempt ', job.id);
        worker.onFailedAttempt(job, errorMessage, doneAttempts);

    }).on('failed', function(errorMessage){
        debug('Job failed ', job.id);
        worker.onFailed(job, errorMessage);

    }).on('progress', function(progress, data){
        debug('\r  job #' + job.id + ' ' + progress + '% complete with data ', data );
        worker.onProgress(job, progress, data);
    });
}


queue.on('job enqueue', function(id, type){
    debug( 'Job %s got queued of type %s', id, type );

}).on('job complete', function(id, result){
    kue.Job.get(id, function(err, job){
        if (err) return;

        if(config.remove_on_complete) {
            job.remove(function(err){
                if (err) throw err;
                    debug('removed completed job #%d', job.id);
            });
        }
    });

}).on( 'error', function( err ) {
    debug( 'Kue: Oops... ', err );
});


// Graceful Shutdown
process.once( 'SIGTERM', function ( sig ) {
    queue.shutdown( 5000, function(err) {
        info( 'Kue shutdown: ', err || '' );
        process.exit( 0 );
    });
});

process.once( 'SIGINT', function ( sig ) {
    queue.shutdown( 5000, function(err) {
        info( 'Kue shutdown: ', err || '' );
        process.exit( 0 );
    });
});

process.once( 'uncaughtException', function(err){
    debug( 'Something bad happened: ', err );
    queue.shutdown( 5000, function(err2){
        debug( 'Kue shutdown result: ', err2 || 'OK' );
        process.exit( 0 );
    });
});


/**************
*** Process the job
**************/

queue.process('status', config.number_of_workers, function(job, done) {
    worker.doSomething(job, done);
});



/***************
*** Success Callback Handlers
***************/


function postLogin(data) { 
    info(data.statusCode + ': successfully logged-in');
    curr_user = data.body;
    executeNextStep();
}


function postGetDevices(data) {
    info(data.statusCode + ': successfully get device list');
    devices = JSON.parse(data.body);
    
    u.each(devices, function(item) {
        if(item[3] === 'camera') {
            cameras.push(item);
        } else if (item[3] === 'bridge') {
            bridges.push(item);
        }
    });
    executeNextStep();
}


function buildPollQuery() {
    var obj = { 'poll': { 'cameras': {} }, 'data': {} };

    u.each(u.filter(cameras, function(item) { return item[5] === 'ATTD' } ), function(item) {
        obj.poll.cameras[item[1]] = { "resource": ["status"] };
    });

    var ee_cookie = een.cookie_jar._jar.store['idx']['eagleeyenetworks.com']['/']['videobank_sessionid'];

    var auth_key = ee_cookie.toString().match(/videobank_sessionid=(c\d*~\w*;)/)[1];

    obj.data.auth_key = auth_key;
    obj.data.active_brand_subdomain = curr_user['active_brand_subdomain'];
    obj.data.active_account_id = curr_user['active_account_id'];

    debug("calling een.subscribeWSPollStream");
    een.subscribeWSPollStream(obj, processWSMessage, processWSError);
    
    info('Subscribing to WS Poll Stream');
}


function processWSMessage(data) {
    debug("called form postSubscribe");
    debug('WS message: ', data);
    compareDeviceStatus(JSON.parse(data));

}


function compareDeviceStatus(data) {
    debug('Calling compareDeviceStatus');
    
    var message = data.data;
    var statusText = '';

    for (var item in message) {

        if(deviceStatus[item] == undefined) {
            deviceStatus[item] = message[item]['status'];
            return
        }

        var oldStatus = deviceStatus[item];
        var newStatus = message[item]['status'];


        if(oldStatus != newStatus) {
            //debug(item + ' status has changed...', oldStatus, newStatus);

            var oldStatusObj = parseStatus(item, oldStatus);
            var newStatusObj = parseStatus(item, newStatus);

            if(newStatusObj['invalid']) {
                // ignore this update that are marked as invalid
                debug('  -> status update marked as invalid', oldStatusObj);
            } else {

                newStatusObj['title'] = undefined;

                if(config.listen_for_recordings) {
                    if(oldStatusObj['recording'] != newStatusObj['recording']) {
                        newStatusObj['title'] = newStatusObj['recording'] ? item + " is now recording" : item + " has stopped recording";
                        createNewJob('status', newStatusObj);
                    }
                }

                if(config.listen_for_cameras_on) {
                    if(oldStatusObj['camera_on'] != newStatusObj['camera_on']) {
                        newStatusObj['title'] =  newStatusObj['camera_on'] ? item + " is now on" : item + " has turned off";
                        createNewJob('status', newStatusObj);
                    }
                }

                if(config.listen_for_streaming) {
                    if(oldStatusObj['streaming'] != newStatusObj['streaming']) {
                        newStatusObj['title'] =  newStatusObj['streaming'] ? item + " is now streaming" : item + " has stopped streaming";
                        createNewJob('status', newStatusObj);
                    }
                }

                if(config.listen_for_registered) {
                    if(oldStatusObj['registered'] != newStatusObj['registered']) {
                        newStatusObj['title'] =  newStatusObj['registered'] ? item + " is now registered" : item + " is no longer registered";
                        createNewJob('status', newStatusObj);
                    }
                }

                if(newStatusObj['title']) {
                    debug(newStatusObj['title']);
                }

            }

            // update the status for the next status change
            deviceStatus[item] = message[item]['status'];

        } else {
            // didn't find a matching status, do nothing
            debug("do nothing ", oldStatus, newStatus);
        }
        
    }

}


function parseStatus(item, status) {
    var status_bits = []
    var status_bit_length = 21;

    for(var i = 0; i < status_bit_length; i++) {
      status_bits.push((parseInt(status) & (1 << status_bit_length - i - 1)) ? true : false);  
    }

    status_bits.reverse();

    var first_thirteen_invalid = status_bits[13] ? true : false;

    var invalid = (status_bits[16]) ? true : false;

    var returned_obj = {
                'device': item,
                'status': status,
                'invalid': invalid,
                'camera_on': !(invalid) ? status_bits[17] : false,
                'streaming': !(invalid) ? status_bits[18] : false,
                'recording': !(invalid) ? status_bits[19] : false,
                'registered': !(invalid) ? status_bits[20] : false
            };
    return returned_obj;
    
}



/***************
*** Error Callback Handlers
***************/

function failure(data) {
    debug(data);
}

function processWSError(data) {
    debug("Error from processWSError: ", data);
}





/*****************
*** Bootstrap the App
*****************/

// start the UI
var app = express();
app.use( kue.app );
app.listen( config.port );
info( 'UI started on port ' + config.port );


executeNextStep();




