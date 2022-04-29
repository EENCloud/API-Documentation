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
print("<li>Frist name: " . $user_obj -> first_name . "</li>");
print("<li>Last name: " . $user_obj -> last_name . "</li>");
print("<li>Email: " . $user_obj -> email . "</li>");
print("<li>Active brand subdomain: " . $user_obj -> active_brand_subdomain . "</li>");
print("<li>Owner Account ID: " . $user_obj -> owner_account_id . "</li>");
print("<li>Active Account ID: " . $user_obj -> active_account_id . "</li>");
print('</ul>');


print('<h1>User Layouts</h1>');
print('<ul>');
foreach($user_obj->layouts as $name => $value) {
        print('<li>'.$name.': '.$value.'</li>');
}
print('</ul>');


print('<h1>User Devices (Attached Cameras)</h1>');
#print($user_devices);
foreach ($user_devices as $dev) {
	if($dev[3] == 'camera' && $dev[5] == 'ATTD') {
		print("<img style='width: 320px;' src=image.php?c=$dev[1]>");
	}
}
print('</ul>');


?>

