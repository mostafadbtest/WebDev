-- phpMyAdmin SQL Dump
-- version 5.2.2
-- https://www.phpmyadmin.net/
--
-- Host: mysql
-- Generation Time: May 11, 2025 at 02:01 PM
-- Server version: 9.3.0
-- PHP Version: 8.2.27

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `company_b`
--

DELIMITER $$
--
-- Procedures
--
CREATE DEFINER=`root`@`%` PROCEDURE `get_users` ()   SELECT * FROM users$$

CREATE DEFINER=`root`@`%` PROCEDURE `get_users_by_name` (IN `name` VARCHAR(20))   SELECT * from users WHERE user_name = name$$

CREATE DEFINER=`root`@`%` PROCEDURE `get_user_name_and_last_name` (IN `user_name` VARCHAR(20), IN `last_name` VARCHAR(20))   SELECT * from users
WHERE user_name = user_name 
AND user_last_name = last_name$$

DELIMITER ;

-- --------------------------------------------------------

--
-- Stand-in structure for view `get_users`
-- (See below for the actual view)
--
CREATE TABLE `get_users` (
`user_pk` bigint unsigned
,`user_username` varchar(20)
,`user_name` varchar(20)
,`user_last_name` varchar(20)
,`user_email` varchar(100)
,`user_password` varchar(255)
,`user_created_at` bigint unsigned
,`user_updated_at` bigint unsigned
,`user_deleted_at` bigint unsigned
);

-- --------------------------------------------------------

--
-- Table structure for table `images`
--

CREATE TABLE `images` (
  `user_fk` bigint UNSIGNED DEFAULT NULL,
  `image_pk` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `image_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `item_fk` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `images`
--

INSERT INTO `images` (`user_fk`, `image_pk`, `image_name`, `item_fk`, `created_at`) VALUES
(80, '877c61679aa245149ad5a8126ab6e476', 'c3edc71122794bc9b5531c120fd52a57.jpg', '52fafc37f6314b50a02052d9aebfa5e1', '2025-05-11 09:18:46'),
(80, 'f034c420e64d4c62a008b9bac38468a2', '8c7521a4fd0448eba84dc54c1fb2dfc9.jpg', '83a6d1444d0d41538ea1a99e4361821a', '2025-05-11 09:18:46');

-- --------------------------------------------------------

--
-- Table structure for table `items`
--

CREATE TABLE `items` (
  `item_pk` char(32) NOT NULL,
  `item_name` varchar(50) NOT NULL,
  `user_pk` bigint UNSIGNED DEFAULT NULL,
  `item_image` varchar(50) NOT NULL,
  `item_price` int UNSIGNED NOT NULL,
  `item_lon` varchar(50) NOT NULL,
  `item_lat` varchar(50) NOT NULL,
  `item_contact_url` varchar(255) DEFAULT NULL,
  `item_description` varchar(255) DEFAULT NULL,
  `item_created_at` bigint UNSIGNED DEFAULT '0',
  `item_updated_at` bigint UNSIGNED DEFAULT '0',
  `item_deleted_at` bigint UNSIGNED DEFAULT '0',
  `item_blocked_at` bigint UNSIGNED DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `items`
--

INSERT INTO `items` (`item_pk`, `item_name`, `user_pk`, `item_image`, `item_price`, `item_lon`, `item_lat`, `item_contact_url`, `item_description`, `item_created_at`, `item_updated_at`, `item_deleted_at`, `item_blocked_at`) VALUES
('1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d', 'Round Tower (Rundetårn).Default Item 1', NULL, 'images/1.jpg', 7, '12.57567', '55.68132', 'https://www.rundetaarn.dk/', 'A 17th-century tower with a spiral ramp and a great city view at the top.', 1746113867, 1746970741, 0, 0),
('52fafc37f6314b50a02052d9aebfa5e1', 'Nyhavn', 80, 'uploads/c3edc71122794bc9b5531c120fd52a57.jpg', 0, '12.59056', '55.67972', 'https://www.visitcopenhagen.com/copenhagen/planning/nyhavn-gdk474735', 'A historic harbor lined with colorful buildings, cozy restaurants, and old wooden ships.', 1746955215, 1746971048, 0, 0),
('71460d8c38584b91a7583832082fc9ad', 'National Museum of Denmark.Default Item 2', NULL, 'images/2.jpg', 21, '12.57472', '55.67472', 'https://shop.natmus.dk/en/collections/nationalmuseet-entrebilletter/products/billet-til-nationalmuseet', 'A large museum with treasures from the Vikings to modern Danish culture.', 1746862257, 1746970741, 0, 0),
('83a6d1444d0d41538ea1a99e4361821a', 'Botanical Garden', 80, 'uploads/8c7521a4fd0448eba84dc54c1fb2dfc9.jpg', 0, '12.57389', '55.68694', 'https://snm.dk/en/botanical-garden', 'A peaceful garden with rare plants, greenhouses, and walking paths in the city center.', 1746955355, 1746956950, 0, 0);

--
-- Triggers `items`
--
DELIMITER $$
CREATE TRIGGER `created_item` BEFORE INSERT ON `items` FOR EACH ROW SET NEW.item_created_at = UNIX_TIMESTAMP()
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `updated_item` BEFORE UPDATE ON `items` FOR EACH ROW SET NEW.item_updated_at = UNIX_TIMESTAMP()
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `roles`
--

CREATE TABLE `roles` (
  `role_pk` int NOT NULL,
  `role_name` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `roles`
--

INSERT INTO `roles` (`role_pk`, `role_name`) VALUES
(1, 'admin'),
(2, 'user');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `user_pk` bigint UNSIGNED NOT NULL,
  `user_username` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `user_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `user_last_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `user_email` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `user_password` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `user_created_at` bigint UNSIGNED NOT NULL DEFAULT '0',
  `user_updated_at` bigint UNSIGNED NOT NULL DEFAULT '0',
  `user_deleted_at` bigint UNSIGNED NOT NULL DEFAULT '0',
  `user_verification_key` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `user_verified_at` int NOT NULL DEFAULT '0',
  `user_reset_key` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `user_delete_key` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `user_blocked_at` bigint DEFAULT '0',
  `role_fk` int DEFAULT '2'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`user_pk`, `user_username`, `user_name`, `user_last_name`, `user_email`, `user_password`, `user_created_at`, `user_updated_at`, `user_deleted_at`, `user_verification_key`, `user_verified_at`, `user_reset_key`, `user_delete_key`, `user_blocked_at`, `role_fk`) VALUES
(80, 'user', 'Coco', 'Cocke', 'user@gmail.com', 'scrypt:32768:8:1$3qtfr5bcv6cQKdjD$50a54a06c69db5983936b38176276694b36777ccac5c44f282f4dffaa33e876b89885d194c1d491e621443031635086a5c175656a9bcc97ce8b5464106bf17c6', 1745679417, 1746640615, 0, '3ff4b089-4f83-4b93-88fb-e7a011a5a35a', 1745679425, NULL, NULL, NULL, 2),
(81, 'Admin', 'Admin', 'Heidari', 'admin@gmail.com', 'scrypt:32768:8:1$NJCrXxWIifliAKy4$c5bf863019579c54e84c8ee7e16dafaec49b22e4150252dd954631ee896fd3af49c6a41fd13d0644cd9e1941510dc7c6504c1deed932fc77558a6dce4905a8b6', 1745679526, 1746620015, 0, '317c4fd3-479e-4c40-bc1a-45569005dc08', 1745679425, NULL, NULL, NULL, 1),
(113, 'xxx', 'xxx', 'xxx', 'xxxxx@yahoo.com', 'scrypt:32768:8:1$3qtfr5bcv6cQKdjD$50a54a06c69db5983936b38176276694b36777ccac5c44f282f4dffaa33e876b89885d194c1d491e621443031635086a5c175656a9bcc97ce8b5464106bf17c6', 1746953377, 0, 0, '4da6776e-e8a5-4a02-9807-54023d7ec5a6', 1746953403, NULL, NULL, NULL, 2);

-- --------------------------------------------------------

--
-- Stand-in structure for view `view_admins`
-- (See below for the actual view)
--
CREATE TABLE `view_admins` (
`user_pk` bigint unsigned
,`user_username` varchar(20)
,`user_name` varchar(20)
,`user_last_name` varchar(20)
,`user_email` varchar(100)
,`user_password` varchar(255)
,`user_created_at` bigint unsigned
,`user_updated_at` bigint unsigned
,`user_deleted_at` bigint unsigned
,`user_verification_key` varchar(36)
,`user_verified_at` int
,`user_reset_key` varchar(36)
,`user_delete_key` varchar(36)
,`user_blocked_at` bigint
,`role_fk` int
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `view_users_blocked`
-- (See below for the actual view)
--
CREATE TABLE `view_users_blocked` (
`user_pk` bigint unsigned
,`user_username` varchar(20)
,`user_name` varchar(20)
,`user_last_name` varchar(20)
,`user_email` varchar(100)
,`user_password` varchar(255)
,`user_created_at` bigint unsigned
,`user_updated_at` bigint unsigned
,`user_deleted_at` bigint unsigned
,`user_verification_key` varchar(36)
,`user_verified_at` int
,`user_reset_key` varchar(36)
,`user_delete_key` varchar(36)
,`user_blocked_at` bigint
,`role_fk` int
);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `images`
--
ALTER TABLE `images`
  ADD PRIMARY KEY (`image_pk`),
  ADD KEY `fk_images_users` (`user_fk`);

--
-- Indexes for table `items`
--
ALTER TABLE `items`
  ADD PRIMARY KEY (`item_pk`),
  ADD KEY `fk_items_users` (`user_pk`);
ALTER TABLE `items` ADD FULLTEXT KEY `item_name` (`item_name`);

--
-- Indexes for table `roles`
--
ALTER TABLE `roles`
  ADD PRIMARY KEY (`role_pk`),
  ADD UNIQUE KEY `role_name` (`role_name`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`user_pk`),
  ADD UNIQUE KEY `user_pk` (`user_pk`),
  ADD UNIQUE KEY `user_username` (`user_username`),
  ADD UNIQUE KEY `user_email` (`user_email`),
  ADD KEY `fk_users_roles` (`role_fk`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `roles`
--
ALTER TABLE `roles`
  MODIFY `role_pk` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `user_pk` bigint UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=114;

-- --------------------------------------------------------

--
-- Structure for view `get_users`
--
DROP TABLE IF EXISTS `get_users`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`%` SQL SECURITY DEFINER VIEW `get_users`  AS SELECT `users`.`user_pk` AS `user_pk`, `users`.`user_username` AS `user_username`, `users`.`user_name` AS `user_name`, `users`.`user_last_name` AS `user_last_name`, `users`.`user_email` AS `user_email`, `users`.`user_password` AS `user_password`, `users`.`user_created_at` AS `user_created_at`, `users`.`user_updated_at` AS `user_updated_at`, `users`.`user_deleted_at` AS `user_deleted_at` FROM `users` ;

-- --------------------------------------------------------

--
-- Structure for view `view_admins`
--
DROP TABLE IF EXISTS `view_admins`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`%` SQL SECURITY DEFINER VIEW `view_admins`  AS SELECT `users`.`user_pk` AS `user_pk`, `users`.`user_username` AS `user_username`, `users`.`user_name` AS `user_name`, `users`.`user_last_name` AS `user_last_name`, `users`.`user_email` AS `user_email`, `users`.`user_password` AS `user_password`, `users`.`user_created_at` AS `user_created_at`, `users`.`user_updated_at` AS `user_updated_at`, `users`.`user_deleted_at` AS `user_deleted_at`, `users`.`user_verification_key` AS `user_verification_key`, `users`.`user_verified_at` AS `user_verified_at`, `users`.`user_reset_key` AS `user_reset_key`, `users`.`user_delete_key` AS `user_delete_key`, `users`.`user_blocked_at` AS `user_blocked_at`, `users`.`role_fk` AS `role_fk` FROM `users` WHERE (`users`.`role_fk` = 1) ;

-- --------------------------------------------------------

--
-- Structure for view `view_users_blocked`
--
DROP TABLE IF EXISTS `view_users_blocked`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`%` SQL SECURITY DEFINER VIEW `view_users_blocked`  AS SELECT `users`.`user_pk` AS `user_pk`, `users`.`user_username` AS `user_username`, `users`.`user_name` AS `user_name`, `users`.`user_last_name` AS `user_last_name`, `users`.`user_email` AS `user_email`, `users`.`user_password` AS `user_password`, `users`.`user_created_at` AS `user_created_at`, `users`.`user_updated_at` AS `user_updated_at`, `users`.`user_deleted_at` AS `user_deleted_at`, `users`.`user_verification_key` AS `user_verification_key`, `users`.`user_verified_at` AS `user_verified_at`, `users`.`user_reset_key` AS `user_reset_key`, `users`.`user_delete_key` AS `user_delete_key`, `users`.`user_blocked_at` AS `user_blocked_at`, `users`.`role_fk` AS `role_fk` FROM `users` WHERE (`users`.`user_blocked_at` <> 0) ;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `images`
--
ALTER TABLE `images`
  ADD CONSTRAINT `fk_images_users` FOREIGN KEY (`user_fk`) REFERENCES `users` (`user_pk`) ON DELETE RESTRICT ON UPDATE RESTRICT;

--
-- Constraints for table `items`
--
ALTER TABLE `items`
  ADD CONSTRAINT `fk_items_users` FOREIGN KEY (`user_pk`) REFERENCES `users` (`user_pk`) ON DELETE RESTRICT ON UPDATE RESTRICT;

--
-- Constraints for table `users`
--
ALTER TABLE `users`
  ADD CONSTRAINT `fk_users_roles` FOREIGN KEY (`role_fk`) REFERENCES `roles` (`role_pk`) ON DELETE RESTRICT ON UPDATE RESTRICT;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
