<?php
$id=$_REQUEST['id'];
$sql="Delete from text where textid='$id'";
$con=mysql_connect("localhost","root","");
$db=mysql_select_db("btwebth",$con);
$rs=mysql_query($sql,$con);
if($rs){
mysql_close($con);
header("Location: update.php");}
?>

