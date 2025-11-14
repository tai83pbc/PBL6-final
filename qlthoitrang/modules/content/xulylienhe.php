<?php 
	include('admincp/modules/config.php');
	$email = $_REQUEST['email'];
	$content = $_REQUEST['content'];
	$idCate = $_REQUEST['idCate'];
	$idProduct = $_REQUEST['idProduct'];

	$sql= "insert into contact(email,content) values('$email','$content')";
	mysqli_query($conn,$sql);
	header("location: ?frame=chitietsp&idCate=$idCate&id=$idProduct");

 ?>