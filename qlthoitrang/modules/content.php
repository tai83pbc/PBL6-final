  <div class="content">           
            <?php
				if(isset($_REQUEST['frame'])){
					$tam= $_REQUEST['frame'];
					switch ($tam) {
						case 'chitietsp':
							include('modules/content/chitietsp.php');
							break;
						case 'loaisp':
							include('modules/content/loaisp.php');
							break;
						case 'dathang':
							include('modules/content/dathang.php');
							break;
						case 'dangkymoi':
								include('modules/content/dangkymoi.php');
								break;
						case 'dangnhap':
							include('modules/content/dangnhap.php');
							break;
						case 'lienhe':
							include('modules/content/lienhe.php');
							break;
						case 'timkiem':
							include('modules/content/timkiem.php');
							break;
						case 'xulylienhe':
							include('modules/content/xulylienhe.php');
							break;
						case 'dangxuat':
							include('modules/content/dangxuat.php');
							break;
						case 'xulybinhluan':
							include('modules/content/xulybinhluan.php');
							break;
						default:
							# code...
							break;
					}
				}
				else{
					include('modules/content/spmoi.php');
				}			
			?>
    
  </div>
        <div class="clear"></div>