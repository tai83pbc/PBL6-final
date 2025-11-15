<?php ob_start();?>
</html>
<head>
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
	<link rel="stylesheet" href="styles.css" type="text/css" />
</head>
	<body>
		<div id="textcontent" style="color:white;width: 700px;height:850px;margin-top: 10px;float: right;border-bottom: 1px solid #fff;border-left: 1px solid #fff;border-right: 1px solid #fff;border-top: 1px solid #fff;background: url(images/content_bg.jpg);background-repeat: repeat-x;">
		<div class="text" style="height:26px;">
		<h4 style="font-size: 16px;height:26px;text-align:left;margin-top:0px;padding-top:0px;">Quản trị</h4>
		</div>
		<div class="textbackground" style="height:813px;" >
		<?php
			if(isset($_SESSION["ad"])){
			?>
				<h3>Đăng nhập thành công</h3>

		<?php
			}
				else{
					echo "Bạn không phải là người quản tri";}
		?>
		</div>
		</div>
	</body>
</html>