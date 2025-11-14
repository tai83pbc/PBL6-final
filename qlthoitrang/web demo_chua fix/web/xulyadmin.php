
<div  style="color:white;width: 700px;height:850px;margin-top: 10px;float: right;border-bottom: 1px solid #fff;border-left: 1px solid #fff;border-right: 1px solid #fff;border-top: 1px solid #fff;background: url(images/content_bg.jpg);background-repeat: repeat-x;">
<div>
<h4 style="text-align:center;height:26px;background: url(images/headline.jpg);color: #fff;padding: 0px;padding-top: 0px;	
padding-bottom: 0px;text-decoration: none;font-size: 16px;background-repeat: repeat-x;margin-bottom: 0px;
margin-left: 0px;margin-right: 0px;margin-top: 0px;border-top: 1px solid #fff;
border-right: 1px solid #fff;border-left: 1px solid #fff;">Thông tin tài khoản</h4></div>
<div style="background-color: #f0f0f0;color: #000;padding: 0px;padding-top: 0px;padding-bottom: 0px;
	margin: 0;border: 1px solid #fff;height:822px;">
<?php
	if(isset($_SESSION["ad"])){
?>
<table align=center>
	<tr>
		<td>
		<?php
			$conn=mysql_connect("localhost", "root", "") ;
			if(!$conn)
				die('can not connect database:'.mysql_error());
			else{
					mysql_select_db("btwebth",$conn);
					$select="select * from account";
					$result=mysql_query($select,$conn);
					$row = mysql_fetch_array($result);
					if($row)	
						{ $select1="select * from account";
							$result1=mysql_query($select1,$conn);
						  ?><br>
						  <table width=600px border=1>
							<tr>
								<td>MTK</td>
								<td>Họ tên</td>
								<td>Địa chỉ</td>
								<td>Số điện thoại</td>
								<td>Email</td>
								<td>Tên tài khoản</td>
								<td>Mật khẩu</td>
								<td>Quyền</td>
							</tr>
							<?php while($row1 = mysql_fetch_array($result1))
								 {?>
							<tr>
								<td>
									<?php echo $row1["cusid"] ?>
								</td>
								<td>
									<?php echo $row1["fullname"] ?>
								</td>
								<td>
									<?php echo $row1["address"] ?>
								</td>
								<td>
									<?php echo $row1["phonenumber"] ?>
								</td>
								<td>
									<?php echo $row1["email"] ?>
								</td>
								<td>
									<?php echo "".$row1["username"] ?>
								</td>
								<td>
									<?php echo $row1["password"] ?>
								</td>
								<td>
									<?php echo $row1["power"] ?>
								</td>
							</tr><?php }?>
							</table> <?php
						}
					else
						echo "Failed";
			}
			mysql_close($conn);
		?>
		</td>
	</tr>
</table>
<?php
	}
	else{
		echo "Bạn không phải là người quản trị";}
?>
</div>
</div>
