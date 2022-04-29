<?php

session_save_path('/var/www/html/tmp');
ini_set('session.gc_probability', 1);

ini_set('display_errors', 'On');
error_reporting(E_ALL);

include('config.php');

class EagleEyeNetworks{

        private $config;

        var $HOST = "https://login.eagleeyenetworks.com";
        var $cookie = '/var/www/html/tmp/cookie.txt';


        function __construct() {
                $current_session = session_id();
                if(empty($current_session)) session_start();

                session_write_close();
                include('config.php');
                $this->config = $config;
        }

        function login() {
                // Step 1 of login process, get token
                $cr = curl_init($this->HOST.'/g/aaa/authenticate');
                $data = array(  'username' => $this->config['username'],
                                'password' => $this->config['password']);

                curl_setopt($cr, CURLOPT_POST, true);
                curl_setopt($cr, CURLOPT_POSTFIELDS, $data);
                curl_setopt($cr, CURLOPT_RETURNTRANSFER, true);
                curl_setopt($cr, CURLOPT_COOKIEJAR, $this->cookie);
                curl_setopt($cr, CURLOPT_COOKIEFILE, $this->cookie);

                $response = curl_exec($cr);
                $obj =  json_decode($response);
                $token = ($obj->{'token'});

                curl_close($cr);

                // Step 2 of login process, exchange token for cookie
                $data = array('token' => $token);

                $cr = curl_init($this->HOST.'/g/aaa/authorize');
                curl_setopt($cr, CURLOPT_POST, true);
                curl_setopt($cr, CURLOPT_POSTFIELDS, $data);
                curl_setopt($cr, CURLOPT_RETURNTRANSFER, true);
                curl_setopt($cr, CURLOPT_COOKIEJAR, $this->cookie);
                curl_setopt($cr, CURLOPT_COOKIEFILE, $this->cookie);

                $user_object = curl_exec($cr);

                curl_close($cr);

                if(isset($user_object)) {
                        return json_decode($user_object);
                } else {
                        return json_decode("[]");
                }
        }

        function list_devices() {
                $cr = curl_init($this->HOST.'/g/list/devices');
                curl_setopt($cr, CURLOPT_RETURNTRANSFER, true);
                curl_setopt($cr, CURLOPT_COOKIEJAR, $this->cookie);
                curl_setopt($cr, CURLOPT_COOKIEFILE, $this->cookie);

                $device_list = curl_exec($cr);
                curl_close($cr);

                if(isset($device_list)) {
                        return json_decode($device_list);
                } else {
                        return json_decode("[]");
                }
        }

        function image($esn, $ts='now', $type='all', $q='high') {
                $cr = curl_init($this->HOST.'/asset/prev/image.jpeg?c='.$esn.';t='.$ts.';q='.$q.';a='.$type);
                curl_setopt($cr, CURLOPT_RETURNTRANSFER, true);
                curl_setopt($cr, CURLOPT_FOLLOWLOCATION, true);
                #curl_setopt($cr, CURLOPT_HEADER, true); #causes image fetch to break
                curl_setopt($cr, CURLINFO_HEADER_OUT, true);
                curl_setopt($cr, CURLOPT_COOKIEJAR, $this->cookie);
                curl_setopt($cr, CURLOPT_COOKIEFILE, $this->cookie);
		$content = curl_exec($cr);
		$info = curl_getinfo($cr);
                curl_close($cr);
		switch($info['http_code']) {
			case 200:
				header('Content-Type: image/jpeg');
				echo $content;
				break;
			case 401:
				header('HTTP/1.0 401 Unauthorized');
                                $this->login();
				break;
			default:
				die('Received response code: ' . $info['http_code']);
		}
                $fp = fopen("/var/www/html/tmp/$esn", "wb");
                fwrite($fp, $content);
                fclose($fp);
        }

        function list_accounts() {
                $cr = curl_init($this->HOST.'/g/account/list');
                curl_setopt($cr, CURLOPT_RETURNTRANSFER, true);
                curl_setopt($cr, CURLOPT_COOKIEJAR, $this->cookie);
                curl_setopt($cr, CURLOPT_COOKIEFILE, $this->cookie);

                $account_list = curl_exec($cr);
                curl_close($cr);

                if(isset($account_list)) {
                        return json_decode($account_list);
                } else {
                        return json_decode("[]");
                }
	}


        function switch_account($account_id) {
                $cr = curl_init($this->HOST.'/g/aaa/switch_account');
                $data = array(  'account_id' => $account_id );

                curl_setopt($cr, CURLOPT_POST, true);
                curl_setopt($cr, CURLOPT_POSTFIELDS, $data);
                curl_setopt($cr, CURLOPT_RETURNTRANSFER, true);
                curl_setopt($cr, CURLOPT_COOKIEJAR, $this->cookie);
                curl_setopt($cr, CURLOPT_COOKIEFILE, $this->cookie);

                $response = curl_exec($cr);
		$obj =  json_decode($response);

		curl_close($cr);

		return $response;

        }









}

?>
