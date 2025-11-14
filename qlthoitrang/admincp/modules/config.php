<?php
	$tenmaychu = 'db_thoitrang';      // Tên service database
	$tentaikhoan = 'user_tt';
	$pass = 'password_tt';
	$csdl = 'web_thoitrang';          // Tên database (MYSQL_DATABASE)

	$conn = mysqli_connect($tenmaychu, $tentaikhoan, $pass, $csdl);

	if (!$conn) {
		die("Kết nối thất bại: " . mysqli_connect_error());
	}
	
	mysqli_set_charset($conn, 'utf8');
?>
