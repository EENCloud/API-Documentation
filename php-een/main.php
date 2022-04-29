<?php

ini_set('display_errors', 'On');
error_reporting(E_ALL);

include('config.php');
include('een.php');

$een = new EagleEyeNetworks();

$user_obj = $een->login();
$user_devices = $een->list_devices();

print('<h1>User Object</h1>');
print('<ul>');
foreach($user_obj as $name => $value) {
	if(is_object($value)) {
		// skip this if its an object
		continue;	
	} else {
        	print('<li>'.$name.': '.$value.'</li>');
	}
}
print('</ul>');

print('<h1>User Layouts</h1>');
print('<ul>');
foreach($user_obj->layouts as $name => $value) {
        print('<li>'.$name.': '.$value.'</li>');
}
print('</ul>');

print('<h1>User Devices (Attached Cameras)</h1>');
foreach ($user_devices as $dev) {
	if($dev[3] == 'camera' && $dev[5] == 'ATTD') {
		print("<img style='width: 320px;' src=image.php?c=$dev[1]>");
	}
}

?>

