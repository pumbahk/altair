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
-- ticketing@dbmain.standby.altrからorganization_id = 15の条件でFamiPortTicketTemplateをdumpしてidをNULLに、organization_idを56に書き換えたもの

LOCK TABLES `FamiPortTicketTemplate` WRITE;
/*!40000 ALTER TABLE `FamiPortTicketTemplate` DISABLE KEYS */;

INSERT INTO FamiPortTicketTemplate (id,template_code,logically_subticket,mappings,organization_id,name) VALUES (NULL,'TTTSTR0001',0,'[["TitleOver","{{{aux.01本券-上タイトル}}}"], ["TitleMain","{{{aux.02本券-本タイトル}}}"], ["TitleSub","{{{aux.03本券-サブタイトル1行目}}}"], ["FreeSpace1","{{{aux.04本券-サブタイトル2行目}}}"], ["FreeSpace2","{{{aux.05本券-サブタイトル3行目}}}"], ["Date","{{{開催日c}}}"], ["OpenTime","{{{開場時刻s}}}{{{aux.06本券-開場表記}}}"], ["StartTime","{{{開始時刻s}}}{{{aux.07本券-開始表記}}}"], ["Price","{{{チケット価格}}}(税込)"], ["Hall","{{{会場名}}}"], ["Note1","{{{aux.08本券-注意事項1行目}}}"], ["Note2","{{{aux.09本券-注意事項2行目}}}"], ["Note3","{{{aux.10本券-注意事項3行目}}}"], ["Note4","{{{aux.11本券-注意事項4行目}}}"], ["Note5","{{{aux.12本券-注意事項5行目}}}"], ["Note6","{{{aux.13本券-注意事項6行目}}}"], ["Note7","{{{aux.14本券-注意事項7行目}}}"], ["Seat1","{{{商品名}}}"], ["Seat2","{{{seatAttributes.gate}}}"], ["Seat3","{{{seatAttributes.block}}}"], ["Seat4","{{#seatAttributes.row}}{{{seatAttributes.row}}}列{{/seatAttributes.row}} {{#seat.seat_no}}{{{seat.seat_no}}}番{{/seat.seat_no}}"], ["Seat5","{{{注文番号}}}-{{{発券番号}}}"], ["Sub-Title1","{{{aux.15半券-タイトル1行目}}}"], ["Sub-Title2","{{{aux.16半券-タイトル2行目}}}"], ["Sub-Title3","{{{aux.17半券-タイトル3行目}}}"], ["Sub-Title4","{{{aux.18半券-タイトル4行目}}}"], ["Sub-Title5","{{{aux.19半券-タイトル5行目}}}"], ["Sub-Date","{{{開催日s}}}"], ["Sub-OpenTime","{{{開場時刻s}}}{{{aux.20半券-開場表記}}}"], ["Sub-StartTime","{{{開始時刻s}}}{{{aux.21半券-開始表記}}}"], ["Sub-Price","{{{チケット価格}}}(税込)"], ["Sub-Seat1","{{{商品名}}}"], ["Sub-Seat2","{{{seatAttributes.gate}}}"], ["Sub-Seat3","{{{seatAttributes.block}}}"], ["Sub-Seat4","{{#seatAttributes.row}}{{{seatAttributes.row}}}列{{/seatAttributes.row}} {{#seat.seat_no}}{{{seat.seat_no}}}番{{/seat.seat_no}}"], ["Sub-Seat5","{{{注文番号}}}-{{{発券番号}}}"]]',56,'TTTSTR0001-BC-01');

INSERT INTO FamiPortTicketTemplate (id,template_code,logically_subticket,mappings,organization_id,name) VALUES (NULL,'TTTSTR0002',0,'[["TitleMain","{{{aux.01本券-メインタイトル}}}"], ["TitleSub","{{{aux.02本券-サブタイトル1行目}}}"], ["Restrictions","{{{aux.03本券-サブタイトル2行目}}}"], ["DetailNote","{{{aux.04本券-注意事項1行目}}}\\n{{{aux.05本券-注意事項2行目}}}\\n{{{aux.06本券-注意事項3行目}}}\\n{{{aux.07本券-注意事項4行目}}}\\n{{{aux.08本券-注意事項5行目}}}\\n{{{aux.09本券-注意事項6行目}}}\\n{{{aux.10本券-注意事項7行目}}}\\n{{{aux.11本券-注意事項8行目}}}\\n{{{aux.12本券-注意事項9行目}}}\\n{{{aux.13本券-注意事項10行目}}}\\n{{{aux.14本券-注意事項11行目}}}"], ["DetailFree","{{{注文番号}}}-{{{発券番号}}}"], ["SeatTicket","{{{商品名}}} {{{seatAttributes.gate}}} {{{seatAttributes.block}}} {{#seatAttributes.row}}{{{seatAttributes.row}}}列{{/seatAttributes.row}} {{#seat.seat_no}}{{{seat.seat_no}}}番{{/seat.seat_no}}"], ["Price","{{{チケット価格}}}(税込)"], ["Inquiry","{{{aux.15本券-お問合せ先}}}"], ["Sub-TitleMain","{{{aux.16半券-タイトル1行目}}}\\n{{{aux.17半券-タイトル2行目}}}\\n{{{aux.18半券-タイトル3行目}}}\\n{{{aux.19半券-タイトル4行目}}}\\n{{{aux.20半券-タイトル5行目}}}\\n{{{aux.21半券-タイトル6行目}}}\\n{{{aux.22半券-タイトル7行目}}}\\n{{{aux.23半券-タイトル8行目}}}\\n{{{aux.24半券-タイトル9行目}}}"], ["Sub-DetailFree","{{{注文番号}}}-{{{発券番号}}}"], ["Sub-Abbreviation","{{{aux.25半券-興行名略称}}}"], ["Sub-Seat","{{{商品名}}}"], ["Sub-Ticket","{{{seatAttributes.gate}}} {{{seatAttributes.block}}} {{#seatAttributes.row}}{{{seatAttributes.row}}}列{{/seatAttributes.row}} {{#seat.seat_no}}{{{seat.seat_no}}}番{{/seat.seat_no}}"], ["Sub-Price","{{{チケット価格}}}(税込)"]]',56,'TTTSTR0002-BC-01');

INSERT INTO FamiPortTicketTemplate (id,template_code,logically_subticket,mappings,organization_id,name) VALUES (NULL,'TTTSTR0003',1,'[["TitleMain","{{{aux.副券01本券-メインタイトル}}}"], ["Free","{{{aux.副券02本券-文言1行目}}}\\n{{{aux.副券03本券-文言2行目}}}\\n{{{aux.副券04本券-文言3行目}}}\\n{{{aux.副券05本券-文言4行目}}}\\n{{{aux.副券06本券-文言5行目}}}\\n{{{aux.副券07本券-文言6行目}}}\\n{{{aux.副券08本券-文言7行目}}}\\n{{{aux.副券09本券-文言8行目}}}\\n{{{aux.副券10本券-文言9行目}}}\\n{{{aux.副券11本券-文言10行目}}}\\n{{{aux.副券12本券-文言11行目}}}\\n{{{aux.副券13本券-文言12行目}}}\\n{{{aux.副券14本券-文言13行目}}}\\n{{{aux.副券15本券-文言14行目}}}\\n{{{aux.副券16本券-文言15行目}}}\\n{{{aux.副券17本券-文言16行目}}}\\n{{{注文番号}}}-{{{発券番号}}}"], ["Sub-Free","{{{aux.副券18半券-文言1行目}}}\\n{{{aux.副券19半券-文言2行目}}}\\n{{{aux.副券20半券-文言3行目}}}\\n{{{aux.副券21半券-文言4行目}}}\\n{{{aux.副券22半券-文言5行目}}}\\n{{{aux.副券23半券-文言6行目}}}\\n{{{aux.副券24半券-文言7行目}}}\\n{{{aux.副券25半券-文言8行目}}}\\n{{{aux.副券26半券-文言9行目}}}\\n{{{aux.副券27半券-文言10行目}}}\\n{{{aux.副券28半券-文言11行目}}}\\n{{{注文番号}}}-{{{発券番号}}}"]]',56,'TTTSTR0003-BC-01');

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