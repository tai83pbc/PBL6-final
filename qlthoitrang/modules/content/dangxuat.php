<?php
	if (isset($_SESSION['login_cus'])) {

     unset($_SESSION['login_cus']);
  }
  header("location: index.php");
?>