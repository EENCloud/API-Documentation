<?php

ini_set('display_errors', 'On');
error_reporting(E_ALL);

include('een.php');

$een = new EagleEyeNetworks();

if(isset($_GET['c'])) $een->image($_GET['c']);

?>

