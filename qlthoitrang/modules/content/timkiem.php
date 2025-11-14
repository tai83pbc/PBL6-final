<?php
	include('admincp/modules/config.php');
  $timkiem = $_REQUEST['timkiem'];
  echo '<pre>Bạn đang tìm kiếm cho '.$timkiem.' </pre>';
	
?>
	<!-- <div class="tieude"> $html .= '<pre>Hello ' . $REQUEST[ 'timkiem' ] . '</pre>';</div> -->
 <ul class="product">
  <?php
  if (isset($timkiem) && $timkiem != null) {
    $sql="select * from product where product_name like '%$timkiem' or product_name like '$timkiem%'";
    $row_moinhat=mysqli_query($conn,$sql);
    $row = mysqli_num_rows($row_moinhat);
    if ($row>0) {
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

  }
   else {
      echo "<span>không có sản phẩm đang tìm</span>";
  }
  }
  else {
      echo "<span>không có sản phẩm đang tìm</span>";
  }
 ?>
</ul>
<div class="clear"></div>