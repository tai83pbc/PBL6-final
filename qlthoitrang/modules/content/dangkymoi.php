<?php
  include('admincp/modules/config.php');

  if (isset($_SESSION['login_cus'])) {
     echo '<script language="javascript">alert("Bạn đã có  tài khoản, bạn muốn đăng kí mới"); 
                    window.location="?frame=dangkymoi";</script>';

     unset($_SESSION['login_cus']);
  }
	if(isset($_REQUEST['gui'])){
		$tenkh=$_REQUEST['hoten'];
		$email=$_REQUEST['email'];
		$diachi=$_REQUEST['diachi'];
		$pass=$_REQUEST['pass'];
		$dienthoai=$_REQUEST['dienthoai'];
    $gioitinh = $_REQUEST['gioitinh'] ;
     $username = $_REQUEST['tendangnhap'] ;

     //bat loi chua nhap du lieu

		$sql_dangky=mysqli_query($conn,"insert into customer (name,email,address,phone_number,sex,username,password) values('$tenkh','$email','$diachi','$dienthoai','$gioitinh','$username','$pass')");
		    
	if($sql_dangky){
		echo '<script language="javascript">alert("Bạn đã đăng kí thành công, vui lòng đăng nhập để thực hiện các chức năng khác"); 
                    window.location="?frame=spmoi";</script>';
	}
	}
?>
	

<div class="tieude">
	 HOAN NGHÊNH QUÝ KHÁCH ĐÃ GHÉ THĂM MINISHOP
</div>
<div class="dangky">
  <p style="font-size:18px; color:red;margin:5px;">Các mục dấu * là bắt buộc tối thiểu. Vui lòng điền đầy đủ và chính xác (Số nhà, Ngõ, thôn xóm/ấp, Phường/xã, huyện/quận, tỉnh, TP)</p>
  <form action="" method="post" enctype="multipart/form-data" >
	<table width="100%" border="1" style="border-collapse:collapse; margin-left: 155px;">
    <tr>
      <td width="40%">Họ tên <strong style="color:red;"> (*)</strong></td>
      <td width="60%"><input type="text" name="hoten" size="50"></td>
    </tr>
    <tr>
      <td>Địa chỉ Email <strong style="color:red;"> (*)</strong></td>
      <td width="60%"><input type="text" name="email" size="50"></td>
    </tr>
    <tr>
      <td>Giới tính <strong style="color:red;"> (*)</strong></td>
      <td width="60%"><select name="gioitinh">
        <option value="nam">nam</option>
        <option value="nữ">nữ</option>
     </select></td>
   </tr>
   <tr>
    <td>tendangnhap <strong style="color:red;"> (*)</strong></td>
    <td width="60%"><input type="text" name="tendangnhap" size="50"></td>
  </tr>
  <tr>
    <td>Mật khẩu  <strong style="color:red;"> (*)</strong></td>
    <td width="60%"><input type="password" name="pass" size="50"></td>
  </tr>
  <tr>
    <td>Điện thoại <strong style="color:red;"> (*)</strong></td>
    <td width="60%"><input type="text" name="dienthoai" size="50"></td>
  </tr>
  <tr>
    <td>Địa chỉ <strong style="color:red;"> (*)</strong></td>
    <td width="60%"><input type="text" name="diachi" size="50"></td>
  </tr>

  <tr>
    <td colspan="2">

     <p><input type="submit" name="gui" value="Đăng ký" /></p>

   </td>
 </tr>
</table>
</form>
