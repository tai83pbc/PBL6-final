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
			$conn=mysql_connect("localhost", "root", "") ;
			if(!$conn)
				die('can not connect database:'.mysql_error());
			else{
					session_start();
					mysql_select_db("btwebth",$conn);
					$t= $_REQUEST["tt"];
					$dc= $_REQUEST["ct"];
					$lc= $_REQUEST["lc"];
					$us= $_SESSION["un"];
					$insert="insert into text(username, title ,content,catid)";
					$insert.=" value('".$us."','".$t."','".$dc."','".$lc."')";
					if(mysql_query($insert,$conn)){
							echo "<h3> Đăng tin thành công" ?>
							<a href=index.php?op=6">Quay về</a> </h3>
						<?php }
					else {
						echo "can not access database";
					//header("Location: index.php?op=2");
					}
					
					
			}
			mysql_close($conn);
		?>
		</td>
	</tr>
</table>
</div>
</div>
