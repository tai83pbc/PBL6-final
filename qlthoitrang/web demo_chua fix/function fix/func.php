<?php
function xoaKiTu($str_in){
$str_out = str_replace("--","",$str_in);
return $str_out;
}
function checkLen($str_in){
if(strlen($str_in)>10)
return false;
else 
return true;
}
?>