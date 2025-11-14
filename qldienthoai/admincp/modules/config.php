<?php
	$tenmaychu='db_dienthoai';
	$tentaikhoan='user_dt';
	$pass='password_dt';
	$csdl='web_dienthoai';
    // LỖI Ở ĐÂY: Dùng hàm mysql_connect đã bị xóa bỏ
	$conn=mysql_connect($tenmaychu,$tentaikhoan,$pass,$csdl) or die('Ko kết nối được'); 
	mysql_select_db($csdl,$conn); // Hàm này cũng là hàm cũ
?>
