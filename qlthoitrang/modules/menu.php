   <div class="menu">
        	<ul>
            	<li><a href="index.php">Trang chủ</a></li>
                <li><a href="?frame=loaisp">Sản phẩm</a></li>
                <li><a href="index.php?frame=dangkymoi">Đăng ký</a></li>
                <li><a href="?frame=dangnhap">Đăng nhập</a></li>
                <li><a href="?frame=dathang">Giỏ hàng</a></li>
                <li><a href="?frame=lienhe">Liên hệ</a></li>
                <div class="search" style=" float: right;">

                <form  action="?frame=timkiem" method="post">
                    <input type="text" placeholder="Search" name = "timkiem" value="">
                    <input type="submit" value="">
                </form>
             </div>

              <?php 
                session_start();
                ?>

                <?php
                
                if (isset($_SESSION['login_cus'])) {
                ?>
                <div style="padding-top: 10px">
                    <span style="color:#fff; font-size:14px; margin-top: 5px">Chào: &ensp;<?php  echo $_SESSION['username']; ?>&ensp;</span>
                    <a href="?frame=dangxuat" style="text-decoration: none; font-size:14px; margin-top: 5px ">  Thoát</a>
                </div>
                    
                    
               <?php
                }
                
                 ?>
         </ul>
        </div>
