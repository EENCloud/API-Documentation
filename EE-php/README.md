## Introduction ##

PHP example for the [Eagle Eye Networks API](https://apidocs.eagleeyenetworks.com).  The wrapper is in `een.php`.

### Docker ###

Check-out `docker-compse.yaml` for details.

Run it with `docker-compose up --build -d`


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

### Diagnostics ###

If you want to see more of what is going on you can copy files from the `diagnostics` folder into the `code` forlder and run them. `main.php` is to see what a user inside of a sub-account can access and  `reseller_main.php` is to see it as a reseller.  Make sure you have the correct user credentials in `config.php` to use these files.
