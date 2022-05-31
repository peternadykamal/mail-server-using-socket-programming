-- phpMyAdmin SQL Dump
-- version 5.1.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: May 31, 2022 at 08:46 AM
-- Server version: 10.4.21-MariaDB
-- PHP Version: 8.0.11

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `mailserverdb`
--

-- --------------------------------------------------------

--
-- Table structure for table `account`
--

CREATE TABLE `account` (
  `account_name` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL
) ;

--
-- Dumping data for table `account`
--

INSERT INTO `account` (`account_name`, `password`) VALUES
('mahmoud3erfan@computerdep.eg', '1234567890'),
('moroelmasery@computerdep.eg', '9876543210'),
('peternady@computerdep.eg', '0123456789'),
('seifossama@computerdep.eg', '9876543210');

-- --------------------------------------------------------

--
-- Table structure for table `email`
--

CREATE TABLE `email` (
  `email_id` int(11) NOT NULL,
  `account_name` varchar(255) NOT NULL,
  `sent_date` datetime DEFAULT current_timestamp(),
  `subject` varchar(255) DEFAULT NULL,
  `body` varchar(510) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `email`
--

INSERT INTO `email` (`email_id`, `account_name`, `sent_date`, `subject`, `body`) VALUES
(3, 'peternady@computerdep.eg', '2022-05-26 08:12:37', 'new email', 'hello seif'),
(5, 'moroelmasery@computerdep.eg', '2022-05-26 08:16:47', 'email subject', 'hello seif and peter'),
(6, 'moroelmasery@computerdep.eg', '2022-05-26 12:44:31', 'another email', 'hello world'),
(7, 'peternady@computerdep.eg', '2022-05-26 12:46:14', 'test email', 'hello from space'),
(8, 'peternady@computerdep.eg', '2022-05-26 13:38:47', 'new email', 'hello seif'),
(10, 'peternady@computerdep.eg', '2022-05-30 13:46:24', 'new email', 'hello seif'),
(71, 'seifossama@computerdep.eg', '2022-05-30 18:26:14', 'sending files', 'test from client side'),
(74, 'seifossama@computerdep.eg', '2022-05-31 08:01:17', 'new email with bash file', 'hellooooo world'),
(75, 'mahmoud3erfan@computerdep.eg', '2022-05-31 08:32:13', 'new email with new files', 'hellooooo team');

-- --------------------------------------------------------

--
-- Table structure for table `file`
--

CREATE TABLE `file` (
  `email_id` int(11) NOT NULL,
  `file_name` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `file`
--

INSERT INTO `file` (`email_id`, `file_name`) VALUES
(71, 'bb.jpg'),
(71, 'time table.pdf'),
(74, 'compileScratch.sh'),
(75, 'CC431 - Sheet 1.pdf'),
(75, 'gKov2He.png');

-- --------------------------------------------------------

--
-- Table structure for table `to_cc_bcc`
--

CREATE TABLE `to_cc_bcc` (
  `email_id` int(11) NOT NULL,
  `account_name` varchar(255) NOT NULL,
  `type` varchar(255) NOT NULL CHECK (`type` in ('to','cc','bcc')),
  `email_type` varchar(255) DEFAULT 'normal'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `to_cc_bcc`
--

INSERT INTO `to_cc_bcc` (`email_id`, `account_name`, `type`, `email_type`) VALUES
(3, 'seifossama@computerdep.eg', 'to', 'normal'),
(5, 'peternady@computerdep.eg', 'bcc', 'archive'),
(5, 'seifossama@computerdep.eg', 'cc', 'normal'),
(6, 'moroelmasery@computerdep.eg', 'bcc', 'normal'),
(6, 'peternady@computerdep.eg', 'cc', 'normal'),
(6, 'seifossama@computerdep.eg', 'to', 'archive'),
(7, 'moroelmasery@computerdep.eg', 'to', 'normal'),
(7, 'peternady@computerdep.eg', 'cc', 'normal'),
(8, 'moroelmasery@computerdep.eg', 'cc', 'normal'),
(8, 'seifossama@computerdep.eg', 'to', 'normal'),
(10, 'peternady@computerdep.eg', 'cc', 'normal'),
(10, 'seifossama@computerdep.eg', 'to', 'normal'),
(71, 'moroelmasery@computerdep.eg', 'to', 'normal'),
(71, 'peternady@computerdep.eg', 'to', 'normal'),
(74, 'mahmoud3erfan@computerdep.eg', 'cc', 'normal'),
(74, 'moroelmasery@computerdep.eg', 'cc', 'normal'),
(74, 'peternady@computerdep.eg', 'to', 'normal'),
(75, 'moroelmasery@computerdep.eg', 'cc', 'normal'),
(75, 'peternady@computerdep.eg', 'bcc', 'normal'),
(75, 'seifossama@computerdep.eg', 'to', 'normal');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `account`
--
ALTER TABLE `account`
  ADD PRIMARY KEY (`account_name`);

--
-- Indexes for table `email`
--
ALTER TABLE `email`
  ADD PRIMARY KEY (`email_id`),
  ADD KEY `account_name` (`account_name`);

--
-- Indexes for table `file`
--
ALTER TABLE `file`
  ADD PRIMARY KEY (`email_id`,`file_name`);

--
-- Indexes for table `to_cc_bcc`
--
ALTER TABLE `to_cc_bcc`
  ADD PRIMARY KEY (`email_id`,`account_name`),
  ADD KEY `account_name` (`account_name`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `email`
--
ALTER TABLE `email`
  MODIFY `email_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=76;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `email`
--
ALTER TABLE `email`
  ADD CONSTRAINT `email_ibfk_1` FOREIGN KEY (`account_name`) REFERENCES `account` (`account_name`) ON DELETE CASCADE;

--
-- Constraints for table `file`
--
ALTER TABLE `file`
  ADD CONSTRAINT `file_ibfk_1` FOREIGN KEY (`email_id`) REFERENCES `email` (`email_id`) ON DELETE CASCADE;

--
-- Constraints for table `to_cc_bcc`
--
ALTER TABLE `to_cc_bcc`
  ADD CONSTRAINT `to_cc_bcc_ibfk_1` FOREIGN KEY (`account_name`) REFERENCES `account` (`account_name`) ON DELETE CASCADE,
  ADD CONSTRAINT `to_cc_bcc_ibfk_2` FOREIGN KEY (`email_id`) REFERENCES `email` (`email_id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
