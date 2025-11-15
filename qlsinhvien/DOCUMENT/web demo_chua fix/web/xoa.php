<?php
$id=$_REQUEST['id'];
$sql="Delete from text where textid='$id'";
$con=mysqli_connect("db_sinhvien", "user_sv", "password_sv", "web_sinhvien");
$db=mysqli_select_db("btwebth",$con);
$rs=mysqli_query($con, $sql);
if($rs){
mysqli_close($con);
header("Location: update.php");}
?>

