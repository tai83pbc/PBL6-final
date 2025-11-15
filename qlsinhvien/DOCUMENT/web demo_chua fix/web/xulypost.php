<div  style="color:white;width: 700px;height:850px;margin-top: 10px;float: right;border-bottom: 1px solid #fff;border-left: 1px solid #fff;border-right: 1px solid #fff;border-top: 1px solid #fff;background: url(images/content_bg.jpg);background-repeat: repeat-x;">
<div>
<h4 style="text-align:left;height:26px;background: url(images/headline.jpg);color: #fff;padding: 0px;padding-top: 0px;	
padding-bottom: 0px;text-decoration: none;font-size: 16px;background-repeat: repeat-x;margin-bottom: 0px;
margin-left: 0px;margin-right: 0px;margin-top: 0px;border-top: 1px solid #fff;
border-right: 1px solid #fff;border-left: 1px solid #fff;">&nbsp;&nbsp;Thông Báo</h4></div>
<div style="background-color: #f0f0f0;color: #000;padding: 0px;padding-top: 0px;padding-bottom: 0px;
	margin: 0;border: 1px solid #fff;height:822px;">
<table align=center>
	<tr>
		<td>
		<?php
			$conn=mysqli_connect("db_sinhvien", "user_sv", "password_sv", "web_sinhvien") ;
			if(!$conn)
				die('can not connect database:'.mysqli_error($conn));
			else{
					session_start();
					mysqli_select_db($conn, "btwebth");
					$t= $_REQUEST["tt"];
					$dc= $_REQUEST["ct"];
					$lc= $_REQUEST["lc"];
					$us= $_SESSION["un"];
					$insert="insert into text(username, title ,content,catid)";
					$insert.=" value('".$us."','".$t."','".$dc."','".$lc."')";
					if(mysqli_query($insert,$conn)){
							echo "<h3> Đăng tin thành công" ?>
							<a href=index.php?op=6">Quay về</a> </h3>
						<?php }
					else {
						echo "can not access database";
					//header("Location: index.php?op=2");
					}
					
					
			}
			mysqli_close($conn);
		?>
		</td>
	</tr>
</table>
</div>
</div>
