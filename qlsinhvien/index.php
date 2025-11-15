<?php
ob_start();
session_start();
?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml"> 
<head>
	<link rel="stylesheet" href="styles.css" type="text/css" />
	<title>New web site</title>
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
</head>

<body>
<div id="all">
	<?php
			include('header.html');
			include('left.php');
			if(!isset($_REQUEST["op"]))
					include('login.html');
					//include('xulyhienthi.php');
			else{
					Switch($_REQUEST["op"]){
						case 1: 
							include('login.html');
							break;
						case 2: 
							include('register.html');
							break;
						case 3:
							include('xulyuser.php');
							break;
						case 4:
							include('xulyadmin.php');
							break;
						case 5:
							include('xulyregis.php');
							break;
						case 6:
							include('dangtin.php');
							break;
						case 7:
							include('xulypost.php');
							break;
						case 8:
							include('quantri.php');
							break;
						case 9:
							include('xulylogout.php');
							break;
						case 10:
							include('capnhat.php');
							break;
						case 11:
							include('update.php');
							break;
						case 12:
							include('tintuc.php');
						case 13:
							include('xulyedit.php');
							break;
						case 14:
							include('xulyhienthi.php');
							break;
					}
				}
			//include('right.html');
			include('footer.html');
	?>
</div>
</html>