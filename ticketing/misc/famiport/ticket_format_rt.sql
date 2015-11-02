-- MySQL dump 10.13  Distrib 5.5.38, for debian-linux-gnu (x86_64)
--
-- Host: dbmain.standby.altr    Database: ticketing
-- ------------------------------------------------------
-- Server version	5.6.17-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `TicketFormat`
--

DROP TABLE IF EXISTS `TicketFormat`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `TicketFormat` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `organization_id` bigint(20) DEFAULT NULL,
  `data` mediumtext NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `deleted_at` timestamp NULL DEFAULT NULL,
  `display_order` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `TicketFormat_ibfk_1` (`organization_id`),
  CONSTRAINT `TicketFormat_ibfk_1` FOREIGN KEY (`organization_id`) REFERENCES `Organization` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=180 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `TicketFormat`
--
-- WHERE:  organization_id = 15 and name like '%TTTSTR%'

LOCK TABLES `TicketFormat` WRITE;
/*!40000 ALTER TABLE `TicketFormat` DISABLE KEYS */;
INSERT INTO `TicketFormat` VALUES (NULL,'TTTSTR0001',15,'{\"print_offset\": {\"y\": \"0mm\", \"x\": \"0mm\"}, \"printable_areas\": [{\"y\": \"5mm\", \"x\": \"23mm\", \"height\": \"54mm\", \"width\": \"112mm\"}, {\"y\": \"5mm\", \"x\": \"141mm\", \"height\": \"54mm\", \"width\": \"36mm\"}], \"perforations\": {\"horizontal\": [], \"vertical\": [\"137mm\"]}, \"aux\": {\"sej_ticket_printer_type\": \"new\", \"famiport_ticket_template_name\": \"TTTSTR0001\"}, \"ticket_image\": \"famiport.png\", \"size\": {\"width\": \"182mm\", \"height\": \"64mm\"}}','2015-07-15 07:22:37','2015-10-01 09:03:06',NULL,100);
INSERT INTO `TicketFormat` VALUES (NULL,'TTTSTR0002',15,'{\"print_offset\": {\"y\": \"0mm\", \"x\": \"0mm\"}, \"printable_areas\": [{\"y\": \"5mm\", \"x\": \"23mm\", \"height\": \"54mm\", \"width\": \"112mm\"}, {\"y\": \"5mm\", \"x\": \"141mm\", \"height\": \"54mm\", \"width\": \"36mm\"}], \"perforations\": {\"horizontal\": [], \"vertical\": [\"137mm\"]}, \"aux\": {\"sej_ticket_printer_type\": \"new\", \"famiport_ticket_template_name\": \"TTTSTR0002\"}, \"ticket_image\": \"famiport.png\", \"size\": {\"width\": \"182mm\", \"height\": \"64mm\"}}','2015-07-15 07:23:26','2015-10-01 09:03:16',NULL,100);
INSERT INTO `TicketFormat` VALUES (NULL,'TTTSTR0003',15,'{\"print_offset\": {\"y\": \"0mm\", \"x\": \"0mm\"}, \"printable_areas\": [{\"y\": \"5mm\", \"x\": \"23mm\", \"height\": \"54mm\", \"width\": \"112mm\"}, {\"y\": \"5mm\", \"x\": \"141mm\", \"height\": \"54mm\", \"width\": \"36mm\"}], \"perforations\": {\"horizontal\": [], \"vertical\": [\"137mm\"]}, \"aux\": {\"sej_ticket_printer_type\": \"new\", \"famiport_ticket_template_name\": \"TTTSTR0003\"}, \"ticket_image\": \"famiport.png\", \"size\": {\"width\": \"182mm\", \"height\": \"64mm\"}}','2015-07-15 07:23:46','2015-10-01 09:03:27',NULL,100);
INSERT INTO `TicketFormat` VALUES (NULL,'TTTSTR0004',15,'{\"print_offset\": {\"y\": \"0mm\", \"x\": \"0mm\"}, \"printable_areas\": [{\"y\": \"5mm\", \"x\": \"23mm\", \"height\": \"54mm\", \"width\": \"112mm\"}, {\"y\": \"5mm\", \"x\": \"141mm\", \"height\": \"54mm\", \"width\": \"36mm\"}], \"perforations\": {\"horizontal\": [], \"vertical\": [\"137mm\"]}, \"aux\": {\"sej_ticket_printer_type\": \"new\", \"famiport_ticket_template_name\": \"TTTSTR0004\"}, \"ticket_image\": \"famiport.png\", \"size\": {\"width\": \"182mm\", \"height\": \"64mm\"}}','2015-07-15 07:24:05','2015-10-01 09:03:39',NULL,100);
INSERT INTO `TicketFormat` VALUES (NULL,'TTTSTR0005',15,'{\"print_offset\": {\"y\": \"0mm\", \"x\": \"0mm\"}, \"printable_areas\": [{\"y\": \"5mm\", \"x\": \"23mm\", \"height\": \"54mm\", \"width\": \"112mm\"}, {\"y\": \"5mm\", \"x\": \"141mm\", \"height\": \"54mm\", \"width\": \"36mm\"}], \"perforations\": {\"horizontal\": [], \"vertical\": [\"137mm\"]}, \"aux\": {\"sej_ticket_printer_type\": \"new\", \"famiport_ticket_template_name\": \"TTTSTR0005\"}, \"ticket_image\": \"famiport.png\", \"size\": {\"width\": \"182mm\", \"height\": \"64mm\"}}','2015-07-15 07:24:29','2015-10-01 09:03:52',NULL,100);
INSERT INTO `TicketFormat` VALUES (NULL,'TTTSTR0006',15,'{\"print_offset\": {\"y\": \"0mm\", \"x\": \"0mm\"}, \"printable_areas\": [{\"y\": \"5mm\", \"x\": \"23mm\", \"height\": \"54mm\", \"width\": \"112mm\"}, {\"y\": \"5mm\", \"x\": \"141mm\", \"height\": \"54mm\", \"width\": \"36mm\"}], \"perforations\": {\"horizontal\": [], \"vertical\": [\"137mm\"]}, \"aux\": {\"sej_ticket_printer_type\": \"new\", \"famiport_ticket_template_name\": \"TTTSTR0006\"}, \"ticket_image\": \"famiport.png\", \"size\": {\"width\": \"182mm\", \"height\": \"64mm\"}}','2015-07-15 07:24:56','2015-10-01 09:04:03',NULL,100);
INSERT INTO `TicketFormat` VALUES (NULL,'TTTSTR0001',15,'{\"printable_areas\": [{\"y\": \"5mm\", \"x\": \"23mm\", \"height\": \"54mm\", \"width\": \"112mm\"}, {\"y\": \"5mm\", \"x\": \"141mm\", \"height\": \"54mm\", \"width\": \"36mm\"}], \"size\": {\"width\": \"182mm\", \"height\": \"64mm\"}, \"perforations\": {\"horizontal\": [], \"vertical\": [\"137mm\"]}, \"print_offset\": {\"y\": \"0mm\", \"x\": \"0mm\"}, \"aux\": {\"famiport_ticket_template_name\": \"TTTSTR0001\"}}','2015-08-26 08:24:12','2015-08-26 08:26:14','2015-08-26 08:26:14',1);
INSERT INTO `TicketFormat` VALUES (NULL,'TTTSTR0001-2',15,'{\"print_offset\": {\"y\": \"0mm\", \"x\": \"0mm\"}, \"printable_areas\": [{\"y\": \"5mm\", \"x\": \"23mm\", \"height\": \"54mm\", \"width\": \"112mm\"}, {\"y\": \"5mm\", \"x\": \"141mm\", \"height\": \"54mm\", \"width\": \"36mm\"}], \"perforations\": {\"horizontal\": [], \"vertical\": [\"137mm\"]}, \"aux\": {\"sej_ticket_printer_type\": \"new\", \"famiport_ticket_template_name\": \"TTTSTR0001-2\"}, \"ticket_image\": \"famiport.png\", \"size\": {\"width\": \"182mm\", \"height\": \"64mm\"}}','2015-08-26 08:30:32','2015-10-01 09:04:12',NULL,100);
INSERT INTO `TicketFormat` VALUES (NULL,'TTTSTR0002-2',15,'{\"print_offset\": {\"y\": \"0mm\", \"x\": \"0mm\"}, \"printable_areas\": [{\"y\": \"5mm\", \"x\": \"23mm\", \"height\": \"54mm\", \"width\": \"112mm\"}, {\"y\": \"5mm\", \"x\": \"141mm\", \"height\": \"54mm\", \"width\": \"36mm\"}], \"perforations\": {\"horizontal\": [], \"vertical\": [\"137mm\"]}, \"aux\": {\"sej_ticket_printer_type\": \"new\", \"famiport_ticket_template_name\": \"TTTSTR0002-2\"}, \"ticket_image\": \"famiport.png\", \"size\": {\"width\": \"182mm\", \"height\": \"64mm\"}}','2015-09-03 06:44:51','2015-10-01 09:04:22',NULL,100);
INSERT INTO `TicketFormat` VALUES (NULL,'TTTSTR0002-2B',15,'{\"print_offset\": {\"y\": \"0mm\", \"x\": \"0mm\"}, \"printable_areas\": [{\"y\": \"5mm\", \"x\": \"23mm\", \"height\": \"54mm\", \"width\": \"112mm\"}, {\"y\": \"5mm\", \"x\": \"141mm\", \"height\": \"54mm\", \"width\": \"36mm\"}], \"perforations\": {\"horizontal\": [], \"vertical\": [\"137mm\"]}, \"aux\": {\"sej_ticket_printer_type\": \"new\", \"famiport_ticket_template_name\": \"TTTSTR0002-2B\"}, \"ticket_image\": \"famiport.png\", \"size\": {\"width\": \"182mm\", \"height\": \"64mm\"}}','2015-10-29 08:38:31','2015-10-29 08:38:53',NULL,100);
/*!40000 ALTER TABLE `TicketFormat` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2015-11-02 21:20:16
-- ticketing@dbmain.standby.altrからFamiPortTicketTemplateをorganization_id = 15 and name like '%TTTSTR%'の条件でdumpしてidをNULLに書き換えたもの