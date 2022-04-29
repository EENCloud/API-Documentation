<?php

ini_set('display_errors', 'On');
error_reporting(E_ALL);

include('config.php');
include('een.php');

$een = new EagleEyeNetworks();

$user_obj = $een->login();
$user_devices = $een->list_devices();

?>

