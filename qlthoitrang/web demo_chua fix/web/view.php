<HTML>
 <HEAD>
  <TITLE> New Document </TITLE>
 <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<style>
.ct{background-color:silver;width:760px;padding:10 10 10 10;float:left}
body{font:normal 14pt  'Times New Roman'; color:navy;margin: 30 30 30 100;background-color:navy}
.title{font:normal  16pt Arial; color:blue}
div.d{width:740px; background-color:#F4F4F4;padding:10 10 10 10}
p{text-align:justify;}
img{float:left; margin-right:10px}
hr{width:720px;float:left}
a.ad:link{font:normal 11pt Arial;color:green;text-decoration:none}
a.ad:activate{font:normal 11pt Arial; color:green;text-decoration:none}
a.ad:hover{font:normal 11pt Arial; color:red;text-decoration:underline}
a.ad:visited{font:normal 11pt Arial; color:green;text-decoration:none}
.title{font:normal  16pt Arial; color:blue}
</style>
<script language=JavaScript>
</script>
 </HEAD>

 <BODY>
<div class=ct>
<div class=d>
<?php
$id=$_REQUEST['id'];
$sql="Select * from text where textid='$id'";
$con=mysql_connect("localhost","root","");
$db=mysql_select_db("btwebth",$con);
mysql_query("SET NAMES 'utf8'");
$rs=mysql_query($sql,$con);
$row=mysql_fetch_array($rs);
?>
	<div>
		<h3 class=title><?php echo $row['title']; ?></h3>
		<p><?php echo $row['content']; ?></p>
	</div>
	<br>
<?php
mysql_close($con);
?>
<!--<a href=news.php> Quay về </a>-->
</div>
</div>
</body>
</html>