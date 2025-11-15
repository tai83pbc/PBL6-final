<div  style="color:white;width: 700px;height:850px;margin-top: 10px;float: right;border-bottom: 1px solid #fff;border-left: 1px solid #fff;border-right: 1px solid #fff;border-top: 1px solid #fff;background: url(images/content_bg.jpg);background-repeat: repeat-x;">
<div>
<h4 style="text-align:center;height:26px;background: url(images/headline.jpg);color: #fff;padding: 0px;padding-top: 0px;	
padding-bottom: 0px;text-decoration: none;font-size: 16px;background-repeat: repeat-x;margin-bottom: 0px;
margin-left: 0px;margin-right: 0px;margin-top: 0px;border-top: 1px solid #fff;
border-right: 1px solid #fff;border-left: 1px solid #fff;">Đăng ký thành công! Dưới đây là thông tin tài khoản của bạn</h4></div>
<div style="background-color: #f0f0f0;color: #000;padding: 0px;padding-top: 0px;padding-bottom: 0px;
	margin: 0;border: 1px solid #fff;height:822px;">
<table align=center>
	<tr>
		<td>
		<?php
    // Kết nối và chọn CSDL trong cùng 1 lệnh. Rất gọn gàng.
    $conn = mysqli_connect("db_sinhvien", "user_sv", "password_sv", "web_sinhvien");

    // Kiểm tra kết nối
    if(!$conn) {
        die('Không thể kết nối database: ' . mysqli_connect_error());
    }
    mysqli_set_charset($conn, 'utf8'); // Nên có để không lỗi font tiếng Việt

    // Dòng "mysqli_select_db" đã bị xóa vì không cần thiết nữa
    // mysqli_select_db($conn, "qlsinhvien"); // <--- SỬA LẠI: Xóa dòng này

    $t = $_REQUEST["fn"];
    $dc = $_REQUEST["ad"];
    $f = $_REQUEST["tel"];
    $e = $_REQUEST["em"];
    $s = $_REQUEST["u"];
    $m = $_REQUEST["ps"];

    // !!! CẢNH BÁO: Lỗ hổng SQL Injection. Rất tốt để làm demo cho PBL
    $insert = "insert into account(fullname,address,phonenumber,email,username,password)";
    $insert .= " value('".$t."','".$dc."','".$f."','".$e."','".$s."','".$m."')";

    // SỬA LẠI: Đảo vị trí $conn và $insert
    if(mysqli_query($conn, $insert)){
            $select = "select * from account where username='$s'";
            
            // SỬA LẠI: Đảm bảo $conn luôn đứng đầu
            $result = mysqli_query($conn, $select);
            $row = mysqli_fetch_array($result);

            if($row) {
                ?>
                <br>
                 <table width=600px border=1>
                <tr>
                    <td>MTK</td>
                    <td>Họ tên</td>
                    <td>Địa chỉ</td>
                    <td>Điện thoại</td>
                    <td>Email</td>
                    <td>Tên tài khoản</td>
                    <td>Mật khẩu</td>
                    <td>Quyền</td>
                </tr>
                <tr>
                    <td><?php echo $row["cusid"] ?></td>
                    <td><?php echo $row["fullname"] ?></td>
                    <td><?php echo $row["address"] ?></td>
                    <td><?php echo $row["phonenumber"] ?></td>
                    <td><?php echo $row["email"] ?></td>
                    <td><?php echo $row["username"] ?></td>
                    <td><?php echo $row["password"] ?></td>
                    <td><?php echo $row["power"] ?></td>
                </tr>
                </table>
                <?php
            } else {
                echo "Không thể truy vấn thông tin tài khoản vừa tạo.";
            }
    } else {
        // Báo lỗi chi tiết từ MySQL
        echo "Lỗi khi đăng ký: " . mysqli_error($conn);
    }

    mysqli_close($conn);
?>
		</td>
	</tr>
</table>
</div>
</div>
