-- phpMyAdmin SQL Dump
-- version 4.9.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Dec 21, 2019 at 05:15 PM
-- Server version: 10.4.8-MariaDB
-- PHP Version: 7.3.10

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `thoitrang`
--

-- --------------------------------------------------------

--
-- Table structure for table `admin`
--

CREATE TABLE `admin` (
  `idAdmin` int(11) NOT NULL,
  `username` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  `password` varchar(50) COLLATE utf8_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dumping data for table `admin`
--

INSERT INTO `admin` (`idAdmin`, `username`, `password`) VALUES
(1, 'admin', 'admin');

-- --------------------------------------------------------

--
-- Table structure for table `category`
--

CREATE TABLE `category` (
  `idCategory` int(11) NOT NULL,
  `category_name` varchar(50) COLLATE utf8_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dumping data for table `category`
--

INSERT INTO `category` (`idCategory`, `category_name`) VALUES
(1, 'Áo sơ mi'),
(2, 'Áo khoác'),
(3, 'Áo len'),
(4, 'Áo chui đầu'),
(6, 'Áo phông'),
(7, 'quần jeans'),
(8, 'Quần vải');

-- --------------------------------------------------------

--
-- Table structure for table `comment`
--

CREATE TABLE `comment` (
  `idComment` int(11) NOT NULL,
  `idProduct` int(11) NOT NULL,
  `content` mediumtext COLLATE utf8_unicode_ci NOT NULL,
  `userName` varchar(50) COLLATE utf8_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dumping data for table `comment`
--

INSERT INTO `comment` (`idComment`, `idProduct`, `content`, `userName`) VALUES
(1, 30, 'Sản phẩm đẹp mắt, giá cả phải chăng', 'quangduy'),
(2, 30, 'sản phẩm vừa túi tiền', 'quangduy98'),
(3, 30, 'đẹp', 'quangduy'),
(5, 31, 'đẹp', 'quangduy');

-- --------------------------------------------------------

--
-- Table structure for table `contact`
--

CREATE TABLE `contact` (
  `idContact` int(11) NOT NULL,
  `email` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  `content` text COLLATE utf8_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dumping data for table `contact`
--

INSERT INTO `contact` (`idContact`, `email`, `content`) VALUES
(27, 'dinhquangduynt@gmail.com', 'Shop nhiệt tình, vui vẻ'),
(28, 'nguyenvana@gmail.com', 'Sản phẩm chất lượng, hợp túi tiền');

-- --------------------------------------------------------

--
-- Table structure for table `customer`
--

CREATE TABLE `customer` (
  `idCus` int(11) NOT NULL,
  `username` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  `password` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  `name` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  `email` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  `sex` bit(1) NOT NULL,
  `address` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  `phone_number` varchar(50) COLLATE utf8_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dumping data for table `customer`
--

INSERT INTO `customer` (`idCus`, `username`, `password`, `name`, `email`, `sex`, `address`, `phone_number`) VALUES
(1, 'quangduy', 'quangduy', 'đinh quang duy', 'dinhquangduynt@gmail.com', b'1', 'nguyễn văn huề, đà nẵng', '0977694163'),
(2, 'quangduy98', 'quanguy', 'Đinh Quang Duy', 'duypro2603@gmail.com', b'1', 'nguyễn văn huề đà nẵng', '0977694163'),
(3, 'admin@gmail.com', 'quangduy', 'Đinh Quang Duydd', 'quangduy', b'1', 'aaa', 'aaaa');

-- --------------------------------------------------------

--
-- Table structure for table `invoice`
--

CREATE TABLE `invoice` (
  `idIncoice` int(11) NOT NULL,
  `name_cus` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  `phone_number` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  `address` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  `status` varchar(50) COLLATE utf8_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `invoice_detail`
--

CREATE TABLE `invoice_detail` (
  `idInvoice` int(11) NOT NULL,
  `idProduct` int(11) NOT NULL,
  `quantity` int(11) NOT NULL,
  `price` varchar(100) COLLATE utf8_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `product`
--

CREATE TABLE `product` (
  `idProduct` int(11) NOT NULL,
  `idCategory` int(11) NOT NULL,
  `product_name` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  `price` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  `description` text COLLATE utf8_unicode_ci NOT NULL,
  `image` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  `quantity` int(11) NOT NULL,
  `day` varchar(50) COLLATE utf8_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dumping data for table `product`
--

INSERT INTO `product` (`idProduct`, `idCategory`, `product_name`, `price`, `description`, `image`, `quantity`, `day`) VALUES
(3, 1, 'Áo sơ mi', '499.000 VND', 'Dáng thông thường(regular)\r\nCó mũ, tay dài', 'somi(1).jpg', 10, '20/10/2019'),
(4, 1, 'Áo sơ mi', '599.000 VND', 'Dáng thông thường(regular)\r\nCó mũ, tay dài', 'somi(2).jpg', 5, '28/10/2019'),
(5, 1, 'Áo sơ mi nam dài tay kẻ caro', '300.000 VND', 'Áo sơ mi Cotton USA kẻ caro.\r\nPhom dáng regular, cổ đức, tay dài, có cúc cài trang trí ở lá cổ.\r\nPhù hợp mặc quanh năm. Mặc thoải mái, dễ chịu có thể kết hợp với quần jeans, khaki.', 'somi(3).jpg', 14, '20/10/2019'),
(6, 1, 'Áo sơ mi nam', '599.000 VND', 'Áo sơ mi bamboo pha kẻ caro.\r\nPhom regular, cổ đức, tay dài.\r\nĐơn giản, lịch sự rất phù hợp mặc nơi công sở. Có thể kết hợp với quần âu, quần khaki, giày tây.', 'somi(4).jpg', 5, '20/10/2019'),
(7, 1, 'Áo sơ mi nam', '300.000 VND', 'Áo sơ mi denim cotton họa tiết kẻ sọc.\r\nPhom regular, cổ đức, tay dài.\r\nCó túi ngực, cài cúc phía trước.\r\nThích hợp mặc quanh năm. Kiểu dáng đơn giản, lịch sự phù hợp nhiều hoàn cảnh.\r\nCó thể phối với nhiều dáng quần: quần jeans, khak, giày lười, giày tây', 'somi(5).jpg', 12, '20/10/2019'),
(8, 1, 'Áo sơ mi nam', '599.000 VND', 'Áo sơ mi cotton kẻ caro.\r\nPhom regular, cổ đức, tay dài.\r\nDòng hàng cơ bản bắt buộc có trong mùa.', 'somi(6).jpg', 20, '20/10/2019'),
(9, 1, 'Áo sơ mi nam', '200.000 VND', 'Áo sơ mi nam', 'somi(7).jpg', 12, '20/10/2019'),
(10, 1, 'Áo sơ mi nam ngắn tay', '215.000 VND', 'Áo sơ mi nam ngắn tay in họa tiết nằm trong bộ sưu tập JOURNEY TO THE EAST\r\nChất liệu linen đặc biệt mềm mại, thoáng mát\r\nVới đặc tính sợi vải không xô dạt, không phai màu nên càng sử dụng lâu, linen càng mềm mại và êm ái hơn\r\n', 'somi(8).jpg', 17, '20/10/2019'),
(11, 2, 'Áo khoác', '400.000 VND', 'Áo khoác nam đen', 'aokhoac(1).jpg', 10, '20/10/2019'),
(12, 2, 'Áo khoác nam', '300.000 VND', 'Áo khoác nam', 'aokhoac(2).jpg', 5, '20/10/2019'),
(13, 2, 'Áo khoác nam', '500.000 VND', 'Dáng thông thường (Regular)\r\nCHẤT LIỆU\r\n100%cotton\r\nGiặt máy ở chế độ nhẹ nhàng, nhiệt độ thông thường\r\nSử dụng hóa chất tẩy không có chất Clo\r\nSấy khô ở nhiệt độ thấp 110°, là ở nhiệt độ trung bình 150°\r\nGiặt với sản phẩm cùng màu\r\nNên phơi vắt ngang', 'aokhoac(3).jpg', 9, '20/10/2019'),
(14, 2, 'Áo khoác nam', '400.000 VND', 'Dáng thông thường (Regular)\r\nCHẤT LIỆU\r\n80% Cotton, 13% Polyester 2% Spandex 5% Latex\r\nGiặt máy ở chế độ nhẹ, nhiệt độ thường\r\nKhông sử dụng hóa chất tẩy có chứa Clo\r\nPhơi trong bóng mát\r\nKhông được sấy, không được là\r\nKhông được giặt khô\r\nGiặt với sản phẩm cùng màu', 'aokhoac(4).jpg', 17, '20/10/2019'),
(15, 2, 'Áo khoác nam', '500.000 VND', 'Dáng thông thường (regular)\r\nSản phẩm có tính năng chống thấm nước\r\nCHẤT LIỆU\r\n100% polyester\r\nGiặt máy nhẹ nhàng, ở nhiệt độ thường\r\nKhông sử dụng hóa chất tẩy\r\nSấy khô nhẹ nhàng, là ở nhiệt độ trung bình 150 độ C\r\nGiặt với sản phẩm cùng màu', 'aokhoac(5).jpg', 13, '20/10/2019'),
(16, 3, 'ÁO GHILE LEN LÔNG CỪU NAM', '400.000 VND', 'Dáng thường (regular)\r\nCHẤT LIỆU\r\n100% Wool\r\nGiặt tay ở nhiệt độ thường, không sử dụng chất tẩy\r\nGiặt mặt trái sản phẩm, phơi phẳng trong bóng mát\r\nKhông được sấy, là nhiệt độ 110 độ C\r\nGiặt với sản phẩm cùng màu', 'aolen(1).jpg', 12, '20/10/2019'),
(17, 3, 'ÁO LEN NAM MỎNG CỔ TRÒN DÀI TAY', '599.000 VND', 'Áo len nam trơn màu\r\nThiết kế cổ tròn, tay và gấu bo gọn gàng\r\nChất liệu mềm mại, ấm áp, không gây tích điện\r\nCHẤT LIỆU\r\n100% Cotton\r\nGiặt máy nhẹ nhàng, ở nhiệt độ thường\r\nKhông sử dụng hóa chất tẩy\r\nSấy khô nhẹ nhàng, là ở nhiệt độ trung bình 150 độ C\r\nGiặt với sản phẩm cùng màu', 'aolen(2).jpg', 12, '20/10/2019'),
(18, 3, 'Áo len nam dài tay cổ tròn', '600.000 VND', 'Áo len nam dệt quả trám\r\nThiết kế cổ tròn, tay và gấu bo gọn gàng\r\nChất liệu mềm mại, ấm áp, không gây tích điện\r\nThông tin người mẫu: 1m82 & 72kg – Size quần 31, size áo: M\r\nCHẤT LIỆU\r\n100% Acrylic\r\nĐể sản phẩm nơi khô ráo\r\nTránh tiếp xúc trực tiếp với ánh nắng mặt trời và nhiệt độ cao\r\nTránh để bề mặt sản phẩm tiếp xúc với các vật sắc nhọn', 'aolen(3).jpg', 9, '20/10/2019'),
(19, 3, 'Áo len nam dài tay cổ tròn', '450.000 VND', 'Áo sơ mi dày cổ tròn dài tay', 'somi(4).jpg', 5, '20/10/2019'),
(20, 4, 'Áo chui dầu dài tay', '125.000 VND', ' Áo chui đầu tay dài, cổ tròn', 'aochuidau(1).jpg', 12, '20/10/2019'),
(21, 4, 'ÁO HOODIES NAM', '449.000 VND', 'Áo hoodies nam dáng regular\r\nCó mũ, tay dài, in hình trẻ trung\r\nChất liệu mềm mại, thấm hút mồ hôi,co giãn thoải mái\r\nCHẤT LIỆU\r\n64% Polyester 34%cotton 2% spandex\r\nGiặt máy nhẹ nhàng, ở nhiệt độ thường\r\nKhông sử dụng hóa chất tẩy\r\nSấy khô nhẹ nhàng, là ở nhiệt độ trung bình 150 độ C\r\nGiặt với sản phẩm cùng màu', 'aochuidau(2).jpg', 12, '20/10/2019'),
(22, 4, 'Áo nỉ chui đầu nam in hình', '399.000 VND', 'Áo nỉ', 'aochuidau(3).jpg', 9, '20/10/2019'),
(23, 6, 'Áo phông dài tay', '120.000 VND', 'Áo thun nam dáng regular, cổ tròn, tay dài, in hình trước ngực\r\nChất liệu mềm mại, co giãn, thấm hút mồ hôi tốt, ít co ngót, bền bỉ theo năm tháng\r\nVải có nguồn gốc là Cotton US, được kiểm soát bởi hiệp hội bông US uy tín, đặc biệt khả năng truy xuất nguồn gốc đáng tin cậy nhất trong các loại bông', 'aophong(1).jpg', 7, '20/10/2019'),
(24, 6, 'Áo phông nam tay dài in hình mickey', '150.000 VND', 'Áo thun nam nằm trong bộ sưu tập Disney-Mickey\r\nDáng áo regular, cổ tròn, tay dài, in hình Mickey\r\nChất liệu Cotton US mềm mại, co giãn, thấm hút mồ hôi tốt\r\nChất liệu ít co ngót, bền bỉ theo năm tháng\r\nVải có nguồn gốc là Cotton US, được kiểm soát bởi hiệp hội bông US uy tín, đặc biệt khả năng truy xuất nguồn gốc đáng tin cậy nhất trong các loại bông', 'aophong(2).jpg', 5, '20/10/2019'),
(25, 6, 'Áo phông ngắn tay', '200.000 VND', ' Áo phông ngắn tay', 'aophong(3).jpg', 7, '20/10/2019'),
(26, 7, 'Quần jean', '500.000 VND', 'Quần jeans Cotton USA.\r\nForm Regular, cạp thường, 5 túi .\r\nCái khoá trước, khuy kim loại.\r\nPhù hợp mặc quanh năm, có thể kết hợp với áo sơ mi, polo, T-shirt, áo len', 'quanjean(1).jpg', 10, '20/10/2019'),
(27, 7, 'Quần jean nam', '600.000 VND', 'Quần jeans cotton co giãn.\r\nPhom slim, cạp thường, 5 túi.\r\nCái khoá trước, khuy kim loại.\r\nHiệu ứng chà bạc.\r\nPhù hợp mặc quanh năm, có thể kết hợp với áo sơ mi, polo, T-shirt, áo len', 'quanjean(2).jpg', 8, '20/10/2019'),
(28, 7, 'Quần jean nam', '760.000 VND', 'Quần jeans cotton có co giãn.\r\nForm slim, cạp thường, 5 túi.\r\nCái khoá trước, khuy kim loại.\r\nPhù hợp mặc quanh năm, có thể kết hợp với áo sơ mi, polo, T-shirt, áo len', 'quanjean(3).jpg', 12, '20/10/2019'),
(29, 8, 'Quần vải nam', '300.000 VND', 'Dáng jogger', 'quanvai(1).jpg', 7, '20/10/2019'),
(30, 8, 'Quần vải nam', '190.000 VND', 'Quần vải nam', 'quanvai(2).jpg', 10, '20/10/2019'),
(31, 8, 'Quần vải nam', '200.000 VND', 'Quần vải nam', 'quanvai(3).jpg', 8, '20/10/2019');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `admin`
--
ALTER TABLE `admin`
  ADD PRIMARY KEY (`idAdmin`);

--
-- Indexes for table `category`
--
ALTER TABLE `category`
  ADD PRIMARY KEY (`idCategory`);

--
-- Indexes for table `comment`
--
ALTER TABLE `comment`
  ADD PRIMARY KEY (`idComment`);

--
-- Indexes for table `contact`
--
ALTER TABLE `contact`
  ADD PRIMARY KEY (`idContact`);

--
-- Indexes for table `customer`
--
ALTER TABLE `customer`
  ADD PRIMARY KEY (`idCus`);

--
-- Indexes for table `invoice`
--
ALTER TABLE `invoice`
  ADD PRIMARY KEY (`idIncoice`);

--
-- Indexes for table `invoice_detail`
--
ALTER TABLE `invoice_detail`
  ADD PRIMARY KEY (`idInvoice`,`idProduct`);

--
-- Indexes for table `product`
--
ALTER TABLE `product`
  ADD PRIMARY KEY (`idProduct`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `admin`
--
ALTER TABLE `admin`
  MODIFY `idAdmin` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `category`
--
ALTER TABLE `category`
  MODIFY `idCategory` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT for table `comment`
--
ALTER TABLE `comment`
  MODIFY `idComment` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `contact`
--
ALTER TABLE `contact`
  MODIFY `idContact` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=30;

--
-- AUTO_INCREMENT for table `customer`
--
ALTER TABLE `customer`
  MODIFY `idCus` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `invoice`
--
ALTER TABLE `invoice`
  MODIFY `idIncoice` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `product`
--
ALTER TABLE `product`
  MODIFY `idProduct` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=32;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
