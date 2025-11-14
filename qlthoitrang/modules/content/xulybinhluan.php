<?php 
	include('admincp/modules/config.php');
	$content = $_REQUEST['textbinhluan'];
	$idProduct = $_REQUEST['idProduct'];
	$idCate = $_REQUEST['idCate'];
	$username = $_SESSION['username'];
	$sql= "insert into comment(idProduct,userName,content) values('$idProduct','$username','$content')";
	mysqli_query($conn,$sql);
	header("location: ?frame=chitietsp&idCate=$idCate&id=$idProduct");

 ?>