<?php
    $tenmaychu = 'db_tracnghiem';
    $tentaikhoan = 'user_tn';
    $pass = 'password_tn';
    $csdl = 'web_tracnghiem';

    // Tạo đối tượng kết nối mới
    $con = new mysqli($tenmaychu, $tentaikhoan, $pass, $csdl);

    // Kiểm tra lỗi kết nối
    if ($con->connect_error) {
        die("Kết nối thất bại: " . $con->connect_error);
    }

    // Thiết lập charset
    $con->set_charset('utf8');
?>
