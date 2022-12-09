  -- phpMyAdmin SQL Dump
  -- version 5.0.2
  -- https://www.phpmyadmin.net/
  --
  -- Host: 127.0.0.1:3306
  -- Generation Time: Mar 28, 2022 at 12:28 AM
  -- Server version: 8.0.21
  -- PHP Version: 7.4.9

  SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
  START TRANSACTION;
  SET time_zone = "+00:00";


  /*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
  /*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
  /*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
  /*!40101 SET NAMES utf8mb4 */;

  --
  -- Database: `payment`
  --

  -- --------------------------------------------------------

  --
  -- Table structure for table `payment`
  --
  CREATE DATABASE IF NOT EXISTS `gym_payment` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
  USE `gym_payment`;

  DROP TABLE IF EXISTS `payment`;
  CREATE TABLE IF NOT EXISTS `payment` (
    `paymentID` int NOT NULL AUTO_INCREMENT,
    `orderID` int NOT NULL,
    `createdTime` datetime NOT NULL,
    `totalPrice` int NOT NULL,
    `sessionID` varchar(1000) DEFAULT NULL,
    `token` varchar(200) NOT NULL,
    PRIMARY KEY (`paymentID`)
  ) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4;

  --
  -- Dumping data for table `payment`
  --

  INSERT INTO `payment` (`paymentID`, `orderID`, `createdTime`, `totalPrice`, `sessionID`, `token`) VALUES
  (1, 1, '2022-03-28 08:24:46', 231913, 'cs_test_a1lqY1b4wC7aqz35FCjTjk8SbrohZ1kpeVE0KIBZV3CJe3UTdglrYflFaS', 'e514fde7-f816-4245-8de8-ca8d08be97e8');
  COMMIT;

  /*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
  /*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
  /*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
