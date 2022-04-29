
# Newer Version #

This has been tested on PHP 5.3, the newer version has been docker-ized and runs on new version of PHP.  You can get it at [mcotton/EE-php](https://github.com/mcotton/EE-php).

## Introduction ##

PHP wrapper for the [Eagle Eye Networks API](https://apidocs.eagleeyenetworks.com).  The wrapper itself is in `een.php` and you can find examples of using in the file `main.php`

### Getting Started ###

    //create a new instance of the API
    $een = new EagleEyeNetworks();


    //supply your EEN credentials in `config.php`
    $username = '<username>';
    $password = '<password>';


    //pass your username/password into the login function and get your user object
    $user_obj = $een->login($username, $password);


    //now that you're logged-in you can get all your devices
    $user_devices = $een->list_devices();


    //you can use page.html and jquery.preview.js to show previews on your site
    $('#preview').cameraPreview({ 'camera_id': '1001abcd' });


### Requirements ###

This was tested using PHP 5.3 and php_curl
