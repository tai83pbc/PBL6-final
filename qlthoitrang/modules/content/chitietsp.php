    <?php
    include('admincp/modules/config.php');
    $idProduct = $_REQUEST['id'];
    $idCate =$_REQUEST['idCate'];
    $sql="select * from product where idProduct=".$idProduct;
    $num=mysqli_query($conn,$sql);
    $dong=mysqli_fetch_array($num,MYSQLI_BOTH);
    ?>

    
    <div class="tieude">Chi tiết sản phẩm</div>

    <div class="box_chitietsp">

     <div class="box_hinhanh">
       <img src="image_minishop/uploads/<?php echo $dong['image'] ?>"   width="200" height="200" />

       <ul class="hinhanhphongto">
         <li><img src="image_minishop/uploads/<?php echo $dong['image'] ?>" id="zoom_01" width="70" height="70" /></li>
       </ul>
     </div>


     <div class="box_info">
       <form action="?frame=chitietsp&idCate=<?php echo $dong['idCategory'] ?>&id=<?php echo $dong['idProduct'] ?>" method="post" enctype="multipart/form-data">
         <p>
           <strong>Tên sản phẩm: </strong><em style="color:red"><?php echo $dong['product_name'] ?></em></p>

           <p><strong>Mã sản phẩm:</strong>  <?php echo $dong['idProduct'] ?> </p> 
           <p><strong>Giá bán:</strong><span style="color:red;"> <?php echo $dong['price']?></span></p> 
           <p style="text-decoration:none;color:blue;"><strong> Tình trạng:</strong> Còn hàng </p> 

           <p><strong>Số lượng:</strong><span> <?php echo $dong['quantity']?></span></p>
           <input type="submit" name="add_to_cart" value="Mua hàng" style="margin:10px;width:100px;height:40px;background:#9F6;color:#000;font-size:18px;border-radius:8px;" />

         </form>              


       </div><!-- Ket thuc box box_info -->

     </div><!-- Ket thuc box chitiet sp -->

     <div class="tabs_panel">
       <ul class="tabs">
         <li rel="panel1" class="active">Thông tin sản phẩm</li>
         <li rel="panel2">Hình ảnh sản phẩm</li>
         <li rel="panel3">Khách hàng đánh giá</li>
         <!-- đánh giá sản phẩm.-->
       </ul>


       <?php
       $sql='select * from product where idProduct='.$idProduct;
       $sql_thongtinsp=mysqli_query($conn,$sql);
       $count_thongtinsp=mysqli_num_rows($sql_thongtinsp);
       if($count_thongtinsp>0){
         $dong_thongtinsp=mysqli_fetch_array($sql_thongtinsp,MYSQLI_BOTH);

         ?>
         <div id="panel1" class="panel active">
           <p><?php echo $dong_thongtinsp['description'] ?></p>

         </div>
         <?php
       }else{
        echo '<p style="padding:30px;">Hiện chưa có thông tin chính thức</p>';
      }
      ?>
      <div id="panel2" class="panel">
       <?php
       $sql = 'select *from product where idProduct='.$idProduct;
       $sql_hinhanhsp=mysqli_query($conn,$sql);
       $count=mysqli_num_rows($sql_hinhanhsp);
       if($count>0){
         while($dong_hinhanhsp=mysqli_fetch_array($sql_hinhanhsp,MYSQLI_BOTH)){

          ?>
          <p style="text-align:center;"><img src="image_minishop/uploads/<?php echo $dong_hinhanhsp['hinhanhsp'] ?>" width="600" height="600" /></p>
          <?php
        }
      }else{
        echo '<p>Chưa có hình ảnh</p>';
      }
      ?>
    </div>

    


    <div id="panel3" class="panel">
      <?php 
      $sql = "select content,userName from comment where idProduct= ".$idProduct;
      $sql_binhluan = mysqli_query($conn,$sql);
      while ($dong=mysqli_fetch_array($sql_binhluan,MYSQLI_BOTH)) {?>
        <div class="binhluan">
          <tr>
            <td><strong><?php echo $dong['userName']?></strong></td>&ensp;&ensp;
            <td><?php echo $dong['content']?></td><br>
          </tr>       
        </div>
        <?php
      }
      ?>

      <?php 
  if (isset($_SESSION['login_cus'])) {
  ?>
  <form action="?frame=xulybinhluan&idCate=<?php echo $idCate ?>&idProduct=<?php echo $idProduct ?>" method="post">
    <input width="100%" type="text" name="textbinhluan" placeholder="bình luận">
  <button type="submit" name="submit_binhluan">Gửi</button>
  </form>
  
  <?php  
  }
  else{
    echo '<a href="?frame=dangnhap&idCate='.$idCate.'&id='. $idProduct.'" style="color:red;">vui lòng đăng nhập để bình luận</a>';

  }

     ?>

    </div>


  </div>


  <!-- san pham lien quan -->
  <?php

  $sql_lienquan="select * from product where idCategory= '$idCate'and idProduct != '$idProduct'";
  $row_lienquan=mysqli_query($conn,$sql_lienquan);

  if($count_lienquan=mysqli_num_rows($row_lienquan)>0){
   ?>
   <div class="sanphamlienquan">
    <div class="tieude">Sản phẩm liên quan</div>
    <ul>
      <?php

      while($dong_lienquan=mysqli_fetch_array($row_lienquan,MYSQLI_BOTH)){
        ?>
        <li><a href="?frame=chitietsp&idCate=<?php echo $dong_lienquan['idCategory'] ?>&id=<?php echo $dong_lienquan['idProduct'] ?>">
         <img src="image_minishop/uploads/<?php echo $dong_lienquan['image'] ?>" width="150" height="150" />
         <p><?php echo $dong_lienquan['product_name'] ?></p>
         <p style="color:red;">Giá : <?php echo $dong_lienquan['price'] ?></p>


       </a></li>
       <?php
     }
     ?>
   </ul>
 </div><!-- Ket thuc box sp liên quan -->
 <?php
}else{
  echo'<div class="tieude">Sản phẩm liên quan</div>';
  echo '<p style="padding:30px;">Hiện chưa có thêm sản phẩm nào</p>';
}
?>
<div class="clear"></div>

