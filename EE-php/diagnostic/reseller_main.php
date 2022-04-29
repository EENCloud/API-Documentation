<?php

ini_set('display_errors', 'On');
error_reporting(E_ALL);

include('config.php');
include('een.php');

$een = new EagleEyeNetworks();

$user_obj = $een->login();
$user_accounts = $een->list_accounts();
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


print('<h1>Sub-Accounts</h1>');
print('<ul>');

foreach ($user_accounts as $account) {

    $een->switch_account($account[0]);

    print('<li>' . $account[1] . ' - ' . $account[0] . '</li>');
    
}
print('</ul>');


foreach ($user_accounts as $account) {

    $een->switch_account($account[0]);

    #print('switching to account: ' . $account[1] . ' - ' . $account[0]);
    
    $user_devices = $een->list_devices();

    print('<h1>User Devices (Attached Cameras) for ' . $account[1] . '</h1>');
    print('<ul>');
    foreach ($user_devices as $dev) {
        if($dev[3] == 'camera' && $dev[5] == 'ATTD') {
            print('<li>' . $dev[2] . ' [' . $dev[1] . ']</li>');
        }
    }
    print('</ul>');


}


?>

