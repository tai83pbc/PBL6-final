
<div class="tieude">
	HOAN NGHÊNH QUÝ KHÁCH ĐÃ GHÉ THĂM MINISHOP
</div>

<div class="dangky">
  <form action="" method="post" enctype="multipart/form-data">
	<table width="500px" border="1" style="border-collapse:collapse; text-align: center; margin-left: 245px">
  <tr>
    <td width="40%">username : <strong style="color:red;"> (*)</strong></td>
    <td width="60%"><input type="text" name="username" size="50"></td>
  </tr>
    <td>Mật khẩu : <strong style="color:red;"> (*)</strong></td>
   <td width="60%"><input type="password" name="pass" size="50"></td>
  </tr>
  <tr>
    <td colspan="2">
    	 
           <p><input type="submit" name="dangnhap" value="Đăng nhập" /></p>
         
    </td>
    </tr>
</table>
</form>

</div>

	<h3><a href="?frame=dangkymoi" style="text-decoration:none;color:#FFF;margin:10px;border-radius:10px;padding:5px;;background:#F00;float:right;" >Đăng ký tài khoản để mua hàng.</a></h3>

<?php
	include('admincp/modules/config.php');
	if (isset($_SESSION['login_cus'])) {
		 echo '<script language="javascript">alert("Bạn đã đăng nhập rồi"); 
                    window.location="?frame=loaisp";</script>';
	}

	if(isset($_REQUEST['dangnhap'])){

		$username=$_REQUEST['username'];
		$pass=$_REQUEST['pass'];
		$sql="select * from customer where username='$username' and password='$pass' limit 1";
		$sql_login=mysqli_query($conn,$sql);
		$count=mysqli_num_rows($sql_login);

		if($count>0){
			$_SESSION['login_cus']="ok";
			$_SESSION['username']=$username;
			
			if(isset($_REQUEST['id']) && isset($_REQUEST['idCate'])){

				$idProduct = $_REQUEST['id'];
				$idCate = $_REQUEST['idCate'];
				header("location: ?frame=chitietsp&idCate=$idCate&id=$idProduct");
			}else{
				header("location: index.php");
			}
			
		}else
		{
			 echo '<script language="javascript">alert("Tài khoản và mật khẩu chưa chính xác!"); 
                    window.location="?frame=dangnhap";</script>';
		}
	}
?>