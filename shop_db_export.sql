-- MariaDB dump 10.19  Distrib 10.4.32-MariaDB, for Linux (x86_64)
--
-- Host: localhost    Database: shop_db
-- ------------------------------------------------------
-- Server version	10.4.32-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `chat_history`
--

DROP TABLE IF EXISTS `chat_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `chat_history` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `chat_id` varchar(50) NOT NULL,
  `role` enum('user','assistant') NOT NULL,
  `message` text NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `idx_chat` (`chat_id`,`created_at`)
) ENGINE=InnoDB AUTO_INCREMENT=223 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `chat_history`
--

LOCK TABLES `chat_history` WRITE;
/*!40000 ALTER TABLE `chat_history` DISABLE KEYS */;
/*!40000 ALTER TABLE `chat_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `chat_sessions`
--

DROP TABLE IF EXISTS `chat_sessions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `chat_sessions` (
  `chat_id` varchar(50) NOT NULL,
  `greeted` tinyint(1) DEFAULT 0,
  `first_seen` timestamp NOT NULL DEFAULT current_timestamp(),
  `last_seen` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`chat_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `chat_sessions`
--

LOCK TABLES `chat_sessions` WRITE;
/*!40000 ALTER TABLE `chat_sessions` DISABLE KEYS */;
INSERT INTO `chat_sessions` VALUES ('996503004660@c.us',1,'2026-04-26 12:47:41','2026-04-26 13:06:57'),('996505342724@s.whatsapp.net',1,'2026-04-26 14:33:57','2026-04-26 14:38:47'),('996550304358@s.whatsapp.net',1,'2026-04-26 14:24:29','2026-04-26 14:25:58'),('996555401237@s.whatsapp.net',1,'2026-04-26 14:18:40','2026-04-26 14:29:41'),('996702041108@s.whatsapp.net',1,'2026-04-26 14:31:03','2026-04-26 15:08:28'),('996703340424@s.whatsapp.net',1,'2026-04-26 14:12:59','2026-04-26 14:27:10'),('996755212525@c.us',1,'2026-04-26 11:35:10','2026-04-26 12:57:52'),('996755212525@s.whatsapp.net',1,'2026-04-26 13:34:01','2026-04-26 14:00:41');
/*!40000 ALTER TABLE `chat_sessions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `products`
--

DROP TABLE IF EXISTS `products`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `products` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `price` int(11) NOT NULL,
  `description` text DEFAULT NULL,
  `category` varchar(100) DEFAULT NULL,
  `in_stock` tinyint(1) DEFAULT 1,
  `photo_url` varchar(500) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `products`
--

LOCK TABLES `products` WRITE;
/*!40000 ALTER TABLE `products` DISABLE KEYS */;
INSERT INTO `products` VALUES (1,'Кроссовки Nike Air Max',5000,'Оригинал, все размеры 38-46, цвета: белый/чёрный','Обувь',1,'https://i.ibb.co/MY2MwXb/nike.jpg'),(2,'Кроссовки Adidas Ultraboost',5500,'Оригинал, амортизация для бега, размеры 39-45','Обувь',1,'https://i.ibb.co/Tqqj6cxp/adidas.jpg'),(3,'Толстовка IT-Style',2500,'100% хлопок, принт не стирается, размеры S/M/L/XL','Одежда',1,'https://i.ibb.co/2YdWJN3Z/hoodie.jpg'),(4,'Футболка IT-Shop Logo',1200,'Хлопок 180г, унисекс, цвета: белый, чёрный, серый','Одежда',1,'https://i.ibb.co/s9XfDh6f/tshirt.jpg'),(5,'Рюкзак Tech Bag',3200,'30L, отсек для ноутбука 15.6\", USB-порт снаружи','Аксессуары',1,'https://i.ibb.co/GvnZ1br9/backpack.jpg'),(6,'Наушники JBL Tune 520BT',4800,'Bluetooth 5.3, до 57 часов работы, складные','Гаджеты',1,'https://i.ibb.co/s936hsy7/jbl.jpg'),(7,'Powerbank 20000 mAh',2900,'Быстрая зарядка 22.5W, 2 USB + Type-C, с дисплеем','Гаджеты',1,'https://i.ibb.co/ZzjY4tsw/powerbank.jpg'),(8,'Мышь игровая Logitech G102',3500,'RGB, 8000 DPI, проводная, для ПК/Mac','Периферия',1,'https://i.ibb.co/5WJXNKQd/mouse.jpg'),(9,'Коврик для мыши XL',800,'80x30 см, тканевый, нескользящее основание','Периферия',1,'https://i.ibb.co/sJtg08Zs/pad.jpg'),(10,'Кабель USB-C 1м 100W',600,'Быстрая зарядка PD, передача данных 480 Mbps','Аксессуары',1,'https://i.ibb.co/xtzF5q10/cable.jpg'),(11,'Веб-камера 1080p',5200,'Full HD 30fps, микрофон, штатив в комплекте','Периферия',1,'https://i.ibb.co/Cgj9x5n/webcam.jpg'),(12,'Клавиатура механическая HyperX',7800,'Switch Blue, RGB подсветка, 104 клавиши, EN/RU','Периферия',1,'https://i.ibb.co/whQ9z9bC/keyboard.jpg'),(13,'Хаб USB-C 7-в-1',3100,'HDMI 4K, 3xUSB 3.0, SD, TF, PD 100W','Аксессуары',1,'https://i.ibb.co/Nd15L1f1/hub.jpg'),(14,'Настройка ПК/ноутбука',1500,'Установка Windows + драйверов + антивируса, выезд в офис','Услуги',1,NULL),(15,'Ремонт телефона',2000,'Замена экрана/батареи, диагностика бесплатно','Услуги',1,NULL);
/*!40000 ALTER TABLE `products` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-04-26 22:23:31
