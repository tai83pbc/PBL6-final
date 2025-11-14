	<?php
	include('admincp/modules/config.php');
	$sql_moinhat="select * from product order by idProduct desc limit 0,6";
	$row_moinhat=mysqli_query($conn,$sql_moinhat);
	
	?>
	<div class="tieude">Sản phẩm mới nhất</div>
	<ul class="product">
		<?php
		while($dong_moinhat=mysqli_fetch_array($row_moinhat,MYSQLI_BOTH)){
			?>
			<li>
				<img src="image_minishop/uploads/<?php echo $dong_moinhat['image'] ?>" width="150" height="150" />
				<p> <a href="?frame=chitietsp&idCate=<?php echo $dong_moinhat['idCategory'] ?>&id=<?php echo $dong_moinhat['idProduct'] ?>" style="color:skyblue"><?php echo $dong_moinhat['product_name'] ?></a></p>
				<p style="color:red;font-weight:bold; border:1px solid #d9d9d9; width:150px;
				height:30px; line-height:30px;margin-left:35px;margin-bottom:5px;"><?php echo $dong_moinhat['price']?></p>
				
				
			</li>
			<?php
		}
		?>
	</ul>
	<div class="clear"></div>

                 <!-- danh dach cac danh muc -->
                 
 <?php
 		$sql_loai=mysqli_query($conn,"select * from category ");
	
	while($dong_loai=mysqli_fetch_array($sql_loai,MYSQLI_BOTH)){
		
			echo '<div class="tieude">'.$dong_loai['category_name'].'</div>';
		 	$sql_loaisp="select * from category inner join product on product.idCategory=category.idCategory where product.idCategory='".$dong_loai['idCategory']."'";
			$row=mysqli_query($conn,$sql_loaisp);
			$count=mysqli_num_rows($row);

			if($count>0){
			?>
  
                	<ul class="product">
                     <?php
			
						while($dong=mysqli_fetch_array($row,MYSQLI_BOTH)){
								
			 		?>
                    	<li>
                        	<img src="image_minishop/uploads/<?php echo $dong['image'] ?>" width="150" height="150" />
                            <p><a href="?frame=chitietsp&idCate=<?php echo $dong['idCategory'] ?>&id=<?php echo $dong['idProduct'] ?>" style="color:skyblue"><?php echo $dong['product_name']?></a></p>
                            <p style="color:red;font-weight:bold; border:1px solid #d9d9d9; width:150px;
                            height:30px; line-height:30px;margin-left:35px;margin-bottom:5px;"><?php echo $dong['price']?></p>
                            
                        	
                        </li>
                        <?php
			}
	}else{
		echo '<h3 style="margin:5px;font-style:italic;color:#000">Hiện chưa có sản phẩm...</h3>';
	}
			
			
						?>
                    </ul>
                     <div class="clear"></div>
                <?php
	
	
	}
	
	
				?>
          
            