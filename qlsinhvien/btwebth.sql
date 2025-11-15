-- phpMyAdmin SQL Dump
-- version 3.2.0.1
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Apr 25, 2011 at 01:07 PM
-- Server version: 5.1.37
-- PHP Version: 5.3.0

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `btwebth`
--

-- --------------------------------------------------------

--
-- Table structure for table `account`
--

CREATE TABLE IF NOT EXISTS `account` (
  `cusid` int(11) NOT NULL AUTO_INCREMENT,
  `fullname` varchar(50) NOT NULL,
  `address` varchar(50) NOT NULL,
  `phonenumber` varchar(25) DEFAULT NULL,
  `email` varchar(25) DEFAULT NULL,
  `username` varchar(25) DEFAULT NULL,
  `password` varchar(25) DEFAULT NULL,
  `power` varchar(25) DEFAULT 'user',
  PRIMARY KEY (`cusid`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=12 ;

--
-- Dumping data for table `account`
--

INSERT INTO `account` (`cusid`, `fullname`, `address`, `phonenumber`, `email`, `username`, `password`, `power`) VALUES
(1, 'Nguyen Cong Hoang', '65-Nguyen Qui Duc', '0905002124', 'nch@yahoo.com', 'Admin', 'admin', 'admin'),
(3, 'Nguyen Ngoc Linh', '108 Ho Xuan Huong', '0906123321', 'linh@yahoo.com', 'linhlogin', '123', 'user'),
(6, 'Ha Duy Son', 'Quang Binh', '0901002003', 'songa@yahoo.com', 'sonlogin', '123456', 'user'),
(7, 'nchoang', '65nqd', '012345', '123@123', 'hlogion', '123456', 'user'),
(8, 'Nguyen Cong Tien', 'CDCN', '0123123321', 'tien@Yahoo.com', 'tienlogin', '123456', 'user'),
(9, 'Nguyen Hoang', '65 NQD', '0905939390', 'hoang@yahoo.com', 'hoang123login', '123456', 'user'),
(10, 'NK', '123', '123123123', '123@yahoo', 'kienlogin', '123456', 'user'),
(11, 'sda', '?a', '122121', '212@ayhoo', 'dung', '123', 'user');

-- --------------------------------------------------------

--
-- Table structure for table `catid`
--

CREATE TABLE IF NOT EXISTS `catid` (
  `catid` int(11) NOT NULL AUTO_INCREMENT,
  `cat` varchar(30) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`catid`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=3 ;

--
-- Dumping data for table `catid`
--

INSERT INTO `catid` (`catid`, `cat`) VALUES
(1, 'Thông báo'),
(2, 'Tin Tức');

-- --------------------------------------------------------

--
-- Table structure for table `text`
--

CREATE TABLE IF NOT EXISTS `text` (
  `textid` int(255) NOT NULL AUTO_INCREMENT,
  `username` varchar(25) NOT NULL,
  `title` varchar(100) NOT NULL,
  `content` text NOT NULL,
  `bydate` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `catid` int(11) NOT NULL,
  PRIMARY KEY (`textid`),
  UNIQUE KEY `textid` (`textid`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=36 ;

--
-- Dumping data for table `text`
--

INSERT INTO `text` (`textid`, `username`, `title`, `content`, `bydate`, `catid`) VALUES
(27, 'admin', 'ThÃ´ng bÃ¡o nghá»‰ há»c Thá»© NÄƒm (14/04/2011) cÃ¡c lá»›p 210SSYS01, 210MMT02, 210MMT03', 'ThÃ´ng bÃ¡o nghá»‰ há»c thá»© NÄƒm (14/04/2011)cÃ¡c lá»›p 210SSYS01, 210MMT02, 210MMT03. LÃ½ do giÃ¡o viÃªn Ä‘i cÃ´ng tÃ¡c.', '2011-04-14 10:17:17', 1),
(28, 'admin', 'ThÃ´ng baÌo Ä‘ÃªÌn tÃ¢Ìt caÌ‰ VÃ¢Ì£n Ä‘Ã´Ì£ng viÃªn tham gia ÄH TDTT ÄHÄN', 'MÆ¡Ì€i tÃ¢Ìt caÌ‰ VÃ¢Ì£n Ä‘Ã´Ì£ng viÃªn (danh saÌch keÌ€m theo) Ä‘uÌng 16h30 ngaÌ€y 15/4/2011 Ä‘ÃªÌn taÌ£i HÃ´Ì£i trÆ°Æ¡Ì€ng Khu B Ä‘ÃªÌ‰ nghe phÃ´Ì‰ biÃªÌn mÃ´Ì£t sÃ´Ì viÃªÌ£c quan troÌ£ng trÆ°Æ¡Ìc khi tham gia ÄaÌ£i hÃ´Ì£i TDTT HSSV ÄHÄN.\r\n', '2011-04-14 10:17:57', 1),
(29, 'admin', 'THÃ”NG BÃO Há»ŒP LIÃŠN CHI ', 'ThÃ´ng bÃ¡o Ä‘áº¿n BCH-BCS cÃ¡c chi Ä‘oÃ n thuá»™c khoa KTXD, Ä‘Ãºng vÃ o lÃºc 16h30, ngÃ y 15/4/2011 (thá»© 6) vá» táº¡i VÄƒn phÃ²ng khoa KTXD Ä‘á»ƒ há»p liÃªn chi. Ná»™i dung: tá»•ng káº¿t chÆ°Æ¡ng trÃ¬nh hoáº¡t Ä‘á»™ng thÃ¡ng 3 vÃ  triá»ƒn khai cÃ´ng tÃ¡c thÃ¡ng 4. Äá» nghá»‹ cÃ¡c chi Ä‘oÃ n tham gia Ä‘Ã´ng Ä‘á»§, Ä‘Ãºng giá».', '2011-04-15 08:48:23', 1),
(34, 'admin', 'ThÃ´ng bÃ¡o kiá»ƒm tra giá»¯a ká»³', 'Tuáº§n sau kiá»ƒm tra giá»¯a ká»³ láº§n 2 ', '2011-04-15 13:29:05', 1);

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
