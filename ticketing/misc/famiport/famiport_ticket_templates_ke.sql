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
-- Dumping data for table `FamiPortTicketTemplate`
--
-- WHERE:  organization_id = 15
-- ticketing@dbmain.standby.altrからorganization_id = 15の条件でFamiPortTicketTemplateをdumpしてidをNULLに、organization_idを36に書き換えたもの

LOCK TABLES `FamiPortTicketTemplate` WRITE;
/*!40000 ALTER TABLE `FamiPortTicketTemplate` DISABLE KEYS */;
INSERT INTO `FamiPortTicketTemplate` VALUES (NULL,'TTTSTR0001',0,'[[\"TitleOver\", \"{{{aux.上タイトル}}}\"], [\"TitleMain\", \"{{{aux.本タイトル}}}\"], [\"TitleSub\", \"{{{aux.サブタイトル}}}\"], [\"FreeSpace1\", \"{{{aux.フリースペース1}}}\"], [\"FreeSpace2\", \"{{{aux.フリースペース2}}}\"], [\"Date\", \"{{{開催日c}}}\"], [\"OpenTime\", \"{{{開場時刻s}}}{{{aux.開場}}}\"], [\"StartTime\", \"{{{開始時刻s}}}{{{aux.開始}}}\"], [\"Price\", \"{{{チケット価格}}}{{{aux.税込表記}}}\"], [\"Hall\", \"{{{会場名}}}\"], [\"Note1\", \"{{{aux.注意事項1}}}\"], [\"Note2\", \"{{{aux.注意事項2}}}\"], [\"Note3\", \"{{{aux.注意事項3}}}\"], [\"Note4\", \"{{{aux.注意事項4}}}\"], [\"Note5\", \"{{{aux.注意事項5}}}\"], [\"Note6\", \"{{{aux.注意事項6}}}\"], [\"Note7\", \"{{{aux.注意事項7}}}\"], [\"Seat1\", \"{{{席種名}}}\"], [\"Seat2\", \"{{{seatAttributes.block}}}\"], [\"Seat3\", \"{{#aux.ゲート表記?}}{{{seatAttributes.gate}}}{{/aux.ゲート表記?}}\"], [\"Seat4\", \"{{{seatAttributes.row}}}{{{aux.列}}} {{{seat.seat_no}}}{{{aux.番}}}\"], [\"Seat5\", \"受付:{{{注文番号}}}\"], [\"Sub-Title1\", \"{{{aux.半券タイトル1}}}\"], [\"Sub-Title2\", \"{{{aux.半券タイトル2}}}\"], [\"Sub-Title3\", \"{{{aux.半券タイトル3}}}\"], [\"Sub-Title4\", \"{{{aux.半券タイトル4}}}\"], [\"Sub-Title5\", \"{{{aux.半券タイトル5}}}\"], [\"Sub-Date\", \"{{{開催日s}}}\"], [\"Sub-OpenTime\", \"{{{開場時刻s}}}{{{aux.開場}}}\"], [\"Sub-StartTime\", \"{{{開始時刻s}}}{{{aux.開始}}}\"], [\"Sub-Price\", \"{{{チケット価格}}}{{{aux.税込表記}}}\"], [\"Sub-Seat1\", \"{{{席種名}}}\"], [\"Sub-Seat2\", \"{{{seatAttributes.block}}}\"], [\"Sub-Seat3\", \"{{#aux.ゲート表記?}}{{{seatAttributes.gate}}}{{/aux.ゲート表記?}}\"], [\"Sub-Seat4\", \"{{{seatAttributes.row}}}{{{aux.列}}} {{{seat.seat_no}}}{{{aux.番}}}\"], [\"Sub-Seat5\", \"受付:{{{注文番号}}}\"]]\n\n',36,'TTTSTR0001-2',NULL);
INSERT INTO `FamiPortTicketTemplate` VALUES (NULL,'TTTSTR0002',0,'[[\"TitleMain\", \"{{{aux.興行メインタイトル}}}\"],[\"TitleSub\", \"{{{aux.興行サブタイトル}}}\"],[\"Restrictions\", \"{{{aux.興行詳細-販売制限}}}\"],[\"DetailNote\", \"{{{aux.興行詳細-注意事項1}}}\\n{{{aux.興行詳細-注意事項2}}}\\n{{{aux.興行詳細-注意事項3}}}\\n{{{aux.興行詳細-注意事項4}}}\\n{{{aux.興行詳細-注意事項5}}}\\n{{{aux.興行詳細-注意事項6}}}\\n{{{aux.興行詳細-注意事項7}}}\\n{{{aux.興行詳細-注意事項8}}}\\n{{{aux.興行詳細-注意事項9}}}\\n{{{aux.興行詳細-注意事項10}}}\\n{{{aux.興行詳細-注意事項11}}}\"],[\"DetailFree\", \"受付：{{{注文番号}}}\"],[\"SeatTicket\", \"{{{券種名}}} {{{seatAttributes.block}}} {{{#aux.ゲート表記?}}}{{{seatAttributes.gate}}}{{{/aux.ゲート表記?}}} {{{seatAttributes.row}}}{{{aux.列}}} {{{seat.seat_no}}}{{{aux.番}}}\"],[\"Price\", \"{{{チケット価格}}}{{{aux.税込表記}}}\"],[\"Inquiry\", \"{{{aux.お問合せ先}}}\"],[\"Sub-TitleMain\", \"{{{aux.半券興行メインタイトル1}}}\\n{{{aux.半券興行メインタイトル2}}}\\n{{{aux.半券興行メインタイトル3}}}\\n{{{aux.半券興行メインタイトル4}}}\\n{{{aux.半券興行メインタイトル5}}}\\n{{{aux.半券興行メインタイトル6}}}\\n{{{aux.半券興行メインタイトル7}}}\\n{{{aux.半券興行メインタイトル8}}}\\n{{{aux.半券興行メインタイトル9}}}\"],[\"Sub-DetailFree\", \"受付:{{{注文番号}}}\"],[\"Sub-Abbreviation\", \"{{{aux.半券興行略称}}}\"],[\"Sub-Seat\", \"{{#aux.商品明細名?}}{{{券種名}}}{{/aux.商品明細名?}}\"],[\"Sub-Ticket\", \"{{{seatAttributes.block}}} {{#aux.ゲート表記?}}{{{seatAttributes.gate}}}{{/aux.ゲート表記?}}\"],[\"Sub-Price\", \"{{{チケット価格}}}{{{aux.税込表記}}}\"]]',36,'TTTSTR0002-2',NULL);
INSERT INTO `FamiPortTicketTemplate` VALUES (NULL,'TTTSTR0003',1,'[[\"TitleMain\", \"{{{aux.副券名}}}\"],[\"Free\", \"{{{aux.注意事項1}}}{{{aux.注意事項2}}}{{{aux.注意事項3}}}{{{aux.注意事項4}}}{{{aux.注意事項5}}}{{{aux.注意事項6}}}{{{aux.注意事項7}}}{{{aux.注意事項8}}}{{{aux.注意事項9}}}{{{aux.注意事項10}}}{{{aux.注意事項11}}}{{{aux.注意事項12}}}{{{aux.注意事項13}}}{{{aux.注意事項14}}}{{{aux.注意事項15}}}{{{aux.注意事項16}}}{{{aux.注意事項17}}}\"],[\"Sub-Free\", \"{{{aux.注意事項18}}}{{{aux.注意事項19}}}{{{aux.注意事項20}}}{{{aux.注意事項21}}}{{{aux.注意事項22}}}{{{aux.注意事項23}}}{{{aux.注意事項24}}}{{{aux.注意事項25}}}{{{aux.注意事項26}}}{{{aux.注意事項27}}}{{{aux.注意事項28}}}{{{aux.注意事項29}}}\"]]',36,'TTTSTR0003',NULL);
INSERT INTO `FamiPortTicketTemplate` VALUES (NULL,'TTTSTR0004',0,'[[\"TitleOver\", \"{{{イベント名}}}\"],[\"TitleMain\", \"{{{パフォーマンス名}}}\"],[\"FreeSpace\", \"{{{aux.FreeSpace1}}} {{{aux.FreeSpace2}}} {{{aux.FreeSpace3}}}\"],[\"Date\", \"{{{開催日}}}\"],[\"OpenTime\", \"{{{開場時刻c}}}開場\"],[\"StartTime\", \"{{{開始時刻c}}}開始\"],[\"Price\", \"{{{チケット価格}}}\"],[\"Hall\", \"{{{会場名}}}\"],[\"Note1-4\", \"{{{aux.注意事項1}}}\\n{{{aux.注意事項2}}}\\n{{{aux.注意事項3}}}\\n{{{aux.注意事項4}}}\"],[\"Note5\", \"{{{aux.注意事項5}}}\"],[\"Note6\", \"{{{aux.注意事項6}}}\"],[\"Note7\", \"{{{aux.注意事項7}}}\"],[\"Seat1\", \"{{{席種名}}}\"],[\"Seat2\", \"{{{席番}}}\"],[\"Seat3\", \"{{{aux.Seat3}}}\"],[\"Seat4\", \"{{{aux.Seat4}}}\"],[\"Seat5\", \"{{{aux.Seat5}}}\"],[\"Sub-Title\", \"{{{パフォーマンス名}}}\"],[\"Sub-Date\", \"{{{開催日}}}\"],[\"Sub-OpenTime\", \"{{{開場時刻c}}}開場\"],[\"Sub-StartTime\", \"{{{開始時刻c}}}開始\"],[\"Sub-Price\", \"{{{チケット価格}}}\"],[\"Sub-Seat1\", \"{{{席種名}}}\"],[\"Sub-Seat2\", \"{{{席番}}}\"],[\"Sub-Seat3\", \"{{{aux.Sub-Seat3}}}\"],[\"Sub-Seat4\", \"{{{aux.Sub-Seat4}}}\"],[\"Sub-Seat5\", \"{{{aux.Sub-Seat5}}}\"]]',36,'TTTSTR0004',NULL);
INSERT INTO `FamiPortTicketTemplate` VALUES (NULL,'TTTSTR0005',0,'[[\"TitleOver\", \"{{{イベント名}}}\"],[\"TitleMain\", \"{{{パフォーマンス名}}}\"],[\"FreeSpace\", \"{{{aux.FreeSpace1}}} {{{aux.FreeSpace2}}} {{{aux.FreeSpace3}}}\"],[\"Date\", \"{{{開催日}}}\"],[\"OpenTime\", \"{{{開場時刻c}}}\"],[\"StartTime\", \"{{{開始時刻c}}}\"],[\"Price\", \"{{{チケット価格}}}\"],[\"Hall\", \"{{{会場名}}}\"],[\"Note1-4\", \"{{{aux.注意事項1-4}}}\"],[\"Note5\", \"{{{aux.注意事項5}}}\"],[\"Note6\", \"{{{aux.注意事項6}}}\"],[\"Note7\", \"{{{aux.注意事項7}}}\"],[\"Seat1\", \"{{{席種名}}}\"],[\"Seat2\", \"{{{席番}}}\"],[\"Seat3\", \"{{{aux.Seat3}}}\"],[\"Seat4\", \"{{{aux.Seat4}}}\"],[\"Seat5\", \"{{{aux.Seat5}}}\"],[\"Sub-Title\", \"{{{パフォーマンス名}}}\"],[\"Sub-Date\", \"{{{開催日}}}\"],[\"Sub-OpenTime\", \"{{{開場時刻c}}}\"],[\"Sub-StartTime\", \"{{{開始時刻c}}}\"],[\"Sub-Price\", \"{{{チケット価格}}}\"],[\"Sub-Seat1\", \"{{{席種名}}}\"],[\"Sub-Seat2\", \"{{{席番}}}\"],[\"Sub-Seat3\", \"{{{aux.Sub-Seat3}}}\"],[\"Sub-Seat4\", \"{{{aux.Sub-Seat4}}}\"],[\"Sub-Seat5\", \"{{{aux.Sub-Seat5}}}\"]]',36,'TTTSTR0005',NULL);
INSERT INTO `FamiPortTicketTemplate` VALUES (NULL,'TTTSTR0006',0,'[[\"TitleOver\", \"{{{イベント名}}}\"],[\"TitleMain\", \"{{{パフォーマンス名}}}\"],[\"FreeSpace\", \"{{{aux.FreeSpace1}}} {{{aux.FreeSpace2}}} {{{aux.FreeSpace3}}}\"],[\"Date\", \"{{{開催日}}}\"],[\"OpenTime\", \"{{{開場時刻c}}}\"],[\"StartTime\", \"{{{開始時刻c}}}\"],[\"Price\", \"{{{チケット価格}}}\"],[\"Hall\", \"{{{会場名}}}\"],[\"Note1-4\", \"{{{aux.注意事項1-4}}}\"],[\"Seat1\", \"{{{席種名}}}\"],[\"Seat2\", \"{{{席番}}}\"],[\"Seat3\", \"{{{aux.Seat3}}}\"],[\"Seat4\", \"{{{aux.Seat4}}}\"],[\"Seat5\", \"{{{aux.Seat5}}}\"],[\"Sub-Title\", \"{{{パフォーマンス名}}}\"],[\"Sub-Date\", \"{{{開催日}}}\"],[\"Sub-OpenTime\", \"{{{開場時刻c}}}\"],[\"Sub-StartTime\", \"{{{開始時刻c}}}\"],[\"Sub-Price\", \"{{{チケット価格}}}\"],[\"Sub-Seat1\", \"{{{席種名}}}\"],[\"Sub-Seat2\", \"{{{席番}}}\"],[\"Sub-Seat3\", \"{{{aux.Sub-Seat3}}}\"],[\"Sub-Seat4\", \"{{{aux.Sub-Seat4}}}\"],[\"Sub-Seat5\", \"{{{aux.Sub-Seat5}}}\"]]',36,'TTTSTR0006',NULL);
/*!40000 ALTER TABLE `FamiPortTicketTemplate` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2015-11-02 13:37:15