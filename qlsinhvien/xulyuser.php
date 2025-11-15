<div  style="color:white;width: 700px;height:850px;margin-top: 10px;float: right;border-bottom: 1px solid #fff;border-left: 1px solid #fff;border-right: 1px solid #fff;border-top: 1px solid #fff;background: url(images/content_bg.jpg);background-repeat: repeat-x;">
<div>
<h4 style="text-align:center;height:26px;background: url(images/headline.jpg);color: #fff;padding: 0px;padding-top: 0px;	
padding-bottom: 0px;text-decoration: none;font-size: 16px;background-repeat: repeat-x;margin-bottom: 0px;
margin-left: 0px;margin-right: 0px;margin-top: 0px;border-top: 1px solid #fff;
border-right: 1px solid #fff;border-left: 1px solid #fff;">Thông tin tài kho?n</h4></div>
<div style="background-color: #f0f0f0;color: #000;padding: 0px;padding-top: 0px;padding-bottom: 0px;
	margin: 0;border: 1px solid #fff;height:822px;">
<table align=center>
	<tr>
		<td>
		<?php
			//session_start();
			unset($_SESSION["ad"]);
			unset($_SESSION["un"]);
			unset($_SESSION["ps"]);
			$conn=mysqli_connect("db_sinhvien", "user_sv", "password_sv", "web_sinhvien");
			if(!$conn)
				die('can not connect database:'.mysqli_error($conn));
			else{
					mysqli_select_db($conn, "qlsinhvien");
					$u=$_REQUEST["user"];
					$p=$_REQUEST["pass"];
					$select="select * from account where username='$u'";
					$result=mysqli_query($conn, $select);
					$row = mysqli_fetch_array($result);
					if($row){
						$select1="select * from account where username='$u' and password= '$p'";
						$result1=mysqli_query($conn, $select1);
						$row1 = mysqli_fetch_array($result1);
						if($row1)	
							{ 
							  $_SESSION["un"]=$u;
							  $_SESSION["ps"]=$p;
							  $_SESSION["id"]=$row1["cusid"];
							  if ($row1["power"]=="admin"){
								  $_SESSION["ad"]="admin";
								  header("Location: index.php?op=8"); 
								 }
							  else{	
								  header("Location:index.php?op=14"); 
									  }
							}
						else
							echo "Sai mật khẩu!!";
						}
					else
						echo "Sai tên tài khoản!!";
			}
			mysqli_close($conn);
		?>
		</td>
	</tr>
</table>
</div>
</div>
