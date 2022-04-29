
(function($) {

    $.fn.cameraPreview = function(options) {

        // use the defaults or customized options if they exist
        var options     =   options || {},
            camera_id   =   options.camera_id || '',
            width       =   options.width || 320,
            height      =   options.height || 180,
            delay       =   options.delay || 1000
            preview     =   new Image(),
            lockout     =   false,
            debug       =   options.debug || false;

        if(!camera_id) {
            // can't do anything without a camera_id
            return false;
        }

        // add preview image to calling div
        this.append(preview);
        if(debug) {
            this.append("<h6 id=" + camera_id + "_debug></h6>");
            $preview_debug = $("#" + camera_id + "_debug");
        }
        $preview = $(preview);

        $preview.width(width + 'px');
        $preview.height(height + 'px');

        function login() {
            if(lockout) {
                // force a 3 second delay between login attempts
                setTimeout(login, 3000)
            } else {
                lockout = true
                $.get('login.php', function() {
                    if(debug) console.log('jQuery.preview: login successful');
                    setTimeout(updatePreview, 0)
                    lockout = false
                });
            }
        }


        function updatePreview() {
            $preview.attr('src', 'image.php?c=' + camera_id + '&rand=' + Math.random());
            $preview.css('background-image', 'url(loading_image.jpg');
            $preview.css('background-position', 'center');
            $preview.css('background-size', 'cover');
            if(debug) {
                console.log('jQuery.preview: new image requested');
                $preview_debug.text("jQuery.preview: new image requested");
            }
        }

        $preview.on('load', function() {
            if(debug) {
                console.log('jQuery.preview: new image loaded');
                $preview_debug.text("jQuery.preview: new image loaded");
            }
            setTimeout(updatePreview, delay)
        });


        $preview.on('error', function() {
            if(debug) {
                console.log('jQuery.preview: image error');
                $preview_debug.text("jQuery.preview: image error");
            }
            login();
        });

        //fetch the first image
        updatePreview();

        //return this to make it chainable
        return this;
    }

}(jQuery));

