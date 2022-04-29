var FileCookiestore = require('tough-cookie-filestore'),
    request = require('request'),
    WebSocket = require('ws'),
    config = require('./config'),
    fs = require('fs'),
    host = 'https://api.eagleeyenetworks.com';

var cookie_path = config.cookie_path || "cookie.json";


// make sure the cookie.json file exists
if(!fs.existsSync(cookie_path)) {
    fs.closeSync(fs.openSync(cookie_path, 'w'));
}

var cookie_jar = request.jar(new FileCookiestore(cookie_path));

// make the cookie jar available outside this module
exports.cookie_jar = cookie_jar;


exports.login = function(opts, success, failure) {
    request.post({
        url: host + '/g/aaa/authenticate',
        jar: cookie_jar,
        json: true,
        headers: {'Authorization': config.api_key },
        body: {
            'username': opts.username,
            'password': opts.password,
            'realm': opts.realm || 'eagleeyenetworks'
        }
        }, function(err, res, body) {
            if (err) { console.log(err,res,body); }
            if (!err && res.statusCode == 200) {
                request.post({
                    url: host + '/g/aaa/authorize',
                    jar: cookie_jar,
                    json: true,
                    headers: {'Authorization': config.api_key },
                    body: { token: res.body.token }
                    }, function(err, res, body) {
                            if (err) { throw new Error('Authorize error') }
                            if (!err && res.statusCode == 200) {
                                // call success callback with user object
                                if ( typeof success === 'function') success(res);
                        }
                })
            } else {
                // call failure callback with status code
                if ( typeof failure === 'function') failure(res);
            }
        }
    )
};

exports.getImage = function(opts, success, failure) {
    var img_url = [   host,
                    '/asset/asset/image.jpeg?c=', opts.c,
                    ';t=', opts.ts || 'now',
                    ';q=', opts.q || 'high',
                    ';a=', opts.a || 'all'
                    ].join('')
    console.log('Requesting image: ' + img_url)
    return  request.get({
                    url: img_url,
                    jar: cookie_jar,
                    headers: {'Authorization': config.api_key }
                },
                function (err, res, body) {
                    if (err) { return err }
                    if (!err && res.statusCode == 200) {}
                    return res
                }
            )

};


exports.getPrevImage = function(opts, success, failure) {
    var img_url = [   host,
                    '/asset/prev/image.jpeg?c=', opts.c,
                    ';t=', opts.ts || 'now',
                    ';q=', opts.q || 'high',
                    ';a=', opts.a || 'all'
                    ].join('')
    console.log('Requesting previous image: ' + img_url)
    return  request.get({
                    url: img_url,
                    jar: cookie_jar,
                    headers: {'Authorization': config.api_key }
                },
                function (err, res, body) {
                    if (err) { return err }
                    if (!err && res.statusCode == 200) {}
                    return res
                }
            )

};

exports.getNextImage = function(opts, success, failure) {
    var img_url = [   host,
                    '/asset/next/image.jpeg?c=', opts.c,
                    ';t=', opts.ts || 'now',
                    ';q=', opts.q || 'high',
                    ';a=', opts.a || 'all'
                    ].join('')
    console.log('Requesting next image: ' + img_url)
    return  request.get({
                    url: img_url,
                    jar: cookie_jar,
                    headers: {'Authorization': config.api_key }
                },
                function (err, res, body) {
                    if (err) { return err }
                    if (!err && res.statusCode == 200) {}
                    return res
                }
            )

};

exports.getAfterImage = function(opts, success, failure) {
    var img_url = [   host,
                '/asset/after/image.jpeg?c=', opts.c,
                ';t=', opts.ts || 'now',
                ';q=', opts.q || 'high',
                ';a=', opts.a || 'all'
                ].join('')
    console.log('Requesting after image: ' + img_url)
    return  request.get({
                url: img_url,
                jar: cookie_jar,
                headers: {'Authorization': config.api_key }
            },
            function (err, res, body) {
                if (err) { return err }
                if (!err && res.statusCode == 200) {}
                return res
            }
        )
};

exports.getVideo = function(opts, success, failure) {
    var src_url = [   host,
                    '/asset/play/video.mp4?c=', opts.c,
                    ';T=', opts.ts || 'now',
                    ';e=', opts.e || 'event',
                    ';q=', opts.a || 'low',
                    ';d=', opts.d || '1'	//download video by default
                    ].join('')
    console.log('Requesting video: ' + src_url)
    return  request.get({
                    url: src_url,
                    jar: cookie_jar,
                    headers: {'Authorization': config.api_key }
                },
                function (err, res, body) {
                    if (err) { return err }
                    if (!err && res.statusCode == 200) {}
                    return res
                }
            )

};


exports.getImageList = function(opts, success, failure) {

};

exports.getVideoList = function(opts, success, failure) {
    var img_url = [   host,
                    '/asset/list/video?c=', opts.c,
                    ';start_timestamp=', opts.start || 'now',
                    ';end_timestamp=', opts.end || 'now',
                    ';q=', opts.q || 'high',
                    ';a=', opts.a || 'all'
                    ].join('')
    console.log('Requesting list of videos: ' + img_url)
    return  request.get({
                    url: img_url,
                    jar: cookie_jar,
                    headers: {'Authorization': config.api_key }
                },
                function (err, res, body) {
                    if (err) { return err }
                    if (!err && res.statusCode == 200) {
                        //console.log('Dumping output from getVideoList before calling success')
                        //console.log(body)
                        //console.log(res.statusCode)
                        if(success) {
                            success(res, body) 
                        }
                    }
                    return res
                }
            )
 
};

exports.getDeviceList = function(opts, success, failure) {
    var src_url = [ host, '/g/device/list'].join('')

    //console.log('making request to getDeviceList: ' + src_url)
    request.get({
            url: src_url,
            jar: cookie_jar,
            headers: {'Authorization': config.api_key }
        },
        function (err, res, body) {
            if (err) { 
                console.log('Error in getDeviceList: ' + err);
                if ( typeof failure === 'function') {
                    failure(res);
                } 
            }
            if (!err && res.statusCode == 200) {
                if ( typeof success === 'function') success(res);
            }
        }
    )

};

exports.subscribePollStream = function(opts, success, failure) {
    var src_url = [ host, '/poll'].join('')

    request.post({
        url: src_url,
        jar: cookie_jar,
        json: true,
        headers: {'Authorization': config.api_key },
        body: opts
        }, function(err, res, body) {
                if (err) { 
                    console.log('Error in getDeviceList: ' + err);
                    if ( typeof failure === 'function') {
                        failure(res);
                    } 
                }
                if (!err && res.statusCode == 200) {
                    // call success callback with user object
                    if ( typeof success === 'function') success(res);
            }
    })
};

exports.subscribeWSPollStream = function(opts, message_func, error_func) {
    var url = ["wss://",
                opts.data.active_brand_subdomain,
                ".eagleeyenetworks.com",
                "/api/v2/Device/",
                opts.data.active_account_id,
                "/Events?A=",
                opts.data.auth_key].join('');

    ws = new WebSocket(url);

    ws.on('open', function() {
        if(config.debug) console.log('WS open');
        try {
            ws.send(JSON.stringify(opts.poll));
        } catch(e) {
            // figure out what to do here
            if ( typeof error_func === 'function') error_func(data);
        }
    });

    ws.on('message', function(data) {
        if(config.debug) console.log('WS message: ', data);
        if ( typeof message_func === 'function') message_func(data);
    });

    ws.on('error', function(data) {
        if(config.debug) console.log('WS Error: ', data)
        if ( typeof error_func === 'function') error_func(data);
    });

    ws.on('close', function close() {
        if(config.debug) console.log('WS close');
        if ( typeof error_func === 'function') error_func({}); 
	process.exit( 0 );
    });
};

exports.continuePolling = function(opts, success, failure) {

};

// archvm01.eagleeyenetworks.com/annotate?c=10042ffd&ts=20140322000104.000&ns=1
exports.addAnnotations = function(opts, success, failure) {
        console.log( [  'http:/','/archvm01.eagleeyenetworks.com', '/annotate?c=', opts.c,
                '&ts=', opts.t, 
                '&ns=', opts.ns 
            ].join(''))
    request.put({
        url: [  'http:/','/archvm01.eagleeyenetworks.com', '/annotate?c=', opts.c,
                '&ts=', opts.ts, 
                '&ns=', opts.ns 
            ].join(''),
        jar: cookie_jar,
        json: true,
        headers: {'Authorization': config.api_key },
        body: opts.body
        },
        function(err, res, body) {
            console.log('return from /annotate:', res.statusCode)
            if(err) { return err }
            if (!err && res.statusCode == 200) {
                if ( typeof success === 'function') success(res.body);
            } else {
                if(typeof failure === 'function') failure(err, res, body);
            }
            return body;
        }
    )
};

exports.DtoS = function(epoch_time) {
    var yy, mm, dd, hr, mn, sc, ms, timecode, jstime;
        jstime = new Date(epoch_time);
        yy = jstime.getUTCFullYear();
        mm = this._padTo2Digits(1 + jstime.getUTCMonth());
        dd = this._padTo2Digits(jstime.getUTCDate());
        hr = this._padTo2Digits(jstime.getUTCHours());
        mn = this._padTo2Digits(jstime.getUTCMinutes());
        sc = this._padTo2Digits(jstime.getUTCSeconds());
        ms = jstime.getUTCMilliseconds();
        if (ms < 10) {
            ms = '00' + ms;
        } else if (ms < 100) {
            ms = '0' + ms;
        }
        timecode = yy + mm + dd + hr + mn + sc + '.' + ms;
        return timecode;
};

exports._padTo2Digits = function(num) {
    return (((num < 10) ? '0' : '') + num);
};

exports.StoD = function (timecode) {
    if(timecode) {
        var yy, mm, dd, hr, mn, sc, ms, jstime;
        yy = parseInt(timecode.substring(0, 4), 10);
        mm = parseInt(timecode.substring(4, 6), 10);
        dd = parseInt(timecode.substring(6, 8), 10);
        hr = parseInt(timecode.substring(8, 10), 10);
        mn = parseInt(timecode.substring(10, 12), 10);
        sc = parseInt(timecode.substring(12, 14), 10);
        ms = parseInt(timecode.substring(15), 10);
        jstime = new Date(Date.UTC(yy, mm - 1, dd, hr, mn, sc, ms));
        return jstime.valueOf();
    }
};

exports.export_cookie_jar = function() {
    return cookie_jar;
};


