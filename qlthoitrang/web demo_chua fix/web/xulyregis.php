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
			$conn=mysql_connect("localhost", "root", "") ;
			if(!$conn)
				die('can not connect database:'.mysql_error());
			else{
					mysql_select_db("btwebth",$conn);
					$t=$_REQUEST["fn"];
					$dc=$_REQUEST["ad"];
					$f=$_REQUEST["tel"];
					$e=$_REQUEST["em"];
					$s=$_REQUEST["u"];
					$m=$_REQUEST["ps"];
					$insert="insert into account(fullname,address,phonenumber,email,username,password)";
					$insert.=" value('".$t."','".$dc."','".$f."','".$e."','".$s."','".$m."')";
					if(mysql_query($insert,$conn)){
							$select="select * from account where username='$s'";
							$result=mysql_query($select,$conn);
							$row = mysql_fetch_array($result);
							if($row)	
							{
								?><br>
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
									<td>
										<?php echo $row["cusid"] ?>
									</td>
									<td>
										<?php echo $row["fullname"] ?>
									</td>
									<td>
										<?php echo $row["address"] ?>
									</td>
									<td>
										<?php echo $row["phonenumber"] ?>
									</td>
									<td>
										<?php echo $row["email"] ?>
									</td>
									<td>
										<?php echo "".$row["username"] ?>
									</td>
									<td>
										<?php echo $row["password"] ?>
									</td>
									<td>
										<?php echo $row["power"] ?>
									</td>
								</tr>
								</table> <?php
						}
						else
							echo "can not access database";
					}
					else{
						//header("Location: index.php?op=2");
						echo "Error: ".mysql_error();
					}
			}
			mysql_close($conn);
		?>
		</td>
	</tr>
</table>
</div>
</div>
