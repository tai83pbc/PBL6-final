<div  style="color:white;width: 700px;height:850px;margin-top: 10px;float: right;border-bottom: 1px solid #fff;border-left: 1px solid #fff;border-right: 1px solid #fff;border-top: 1px solid #fff;background: url(images/content_bg.jpg);background-repeat: repeat-x;">
<div>
<h4 style="text-align:left;height:26px;background: url(images/headline.jpg);color: #fff;padding: 0px;padding-top: 0px;	
padding-bottom: 0px;text-decoration: none;font-size: 16px;background-repeat: repeat-x;margin-bottom: 0px;
margin-left: 0px;margin-right: 0px;margin-top: 0px;border-top: 1px solid #fff;
border-right: 1px solid #fff;border-left: 1px solid #fff;">&nbsp;&nbsp;Thông báo</h4></div>
<div style="background-color: #f0f0f0;color: #000;padding: 0px;padding-top: 0px;padding-bottom: 0px;
	margin: 0;border: 1px solid #fff;height:822px;">
<table align=center>
	<tr>
		<td>
		<?php
		$id=$_REQUEST['textid'];
		$tit=$_REQUEST['title'];
		$cnt=$_REQUEST['ctent'];
		if($id!=""){
			$sql="Update text set title='$tit',content='$cnt' where textid='$id'";
			$con=mysql_connect("localhost","root","");
			$db=mysql_select_db("btwebth",$con);
			$rs=mysql_query($sql,$con);
			if($rs)
				echo "<h3> Sửa tin thành công" ;
			else 
				echo "<h3>Không thành công";
			mysql_close($con);
			}
		else 
			echo "<h3>Chưa chọn tin ";
		?>
		<a href=update.php?id">Quay về</a></h3>
	</td>
	</tr>
</table>
</div>
</div>