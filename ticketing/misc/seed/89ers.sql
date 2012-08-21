BEGIN;

-- INSERT INTO `OperatorRole` (id, name, status) VALUES (1, 'administrator', 1);
-- INSERT INTO `OperatorRole` (id, name, status) VALUES (2, 'superuser', 1);
-- INSERT INTO `DeliveryMethodPlugin` VALUES (1, '郵送','2012-07-10 17:44:29','2012-07-10 17:44:29', NULL);
-- INSERT INTO `PaymentMethodPlugin` VALUES (1, 'クレジットカード払い','2012-07-10 17:44:29','2012-07-10 17:44:29', NULL);
-- INSERT INTO `PaymentMethodPlugin` VALUES (3, 'セブンイレブン支払い','2012-07-10 17:44:29','2012-07-10 17:44:29', NULL);


INSERT INTO `User` (id) VALUES (65);
INSERT INTO `User` (id) VALUES (66);
INSERT INTO `Organization` VALUES (10,'BJ89ers','B8',1,'89ers@ticketstar.jp','','','','','','','',65,'',1,'2012-07-10 17:44:29','2012-07-10 17:44:29',NULL);
INSERT INTO `Organization` VALUES (11,'秋田ノーザンハピネッツ','DD',1,'rt_support@ticketstar.jp','秋田','秋田','秋田','秋田','','','',66,'',NULL,'2012-07-18 04:20:34','2012-07-18 04:20:34',NULL);
INSERT INTO `SejTenant` VALUES (1, '仙台89ERS（ナイナーズチケット）', 30520, '022-215-8138','仙台89ERS チケット事務局', NULL, NULL, 10, NOW(), NULL, NULL);
INSERT INTO `SejTenant` VALUES (2, '秋田ノーザンハピネッツ', 30520, '','', NULL, NULL, 11, NOW(), NULL, NULL);

INSERT INTO `Account` VALUES (100000,NULL,'BJ89ers',65,10,'2012-07-11 05:32:51','2012-07-11 05:32:51',NULL);
INSERT INTO `Account` VALUES (100001,NULL,'NH',66,11,'2012-07-18 12:27:32','2012-07-18 12:27:32',NULL);
INSERT INTO `Event` VALUES (100001,'BJ890','仙台89ers FC会員登録','bj89ers',100000,10,'2012-07-10 17:44:29','2012-07-10 17:44:29',NULL);
INSERT INTO `Membership` VALUES (100001,'89ers',NULL,NULL,NULL);
INSERT INTO `MemberGroup` (id, name, membership_id) VALUES(100001, 'corporation', 100001);
INSERT INTO `MemberGroup` (id, name, membership_id) VALUES(100002, 'platinum', 100001);
INSERT INTO `MemberGroup` (id, name, membership_id) VALUES(100003, 'gold', 100001);
INSERT INTO `MemberGroup` (id, name, membership_id) VALUES(100009, 'guest', 100001);

INSERT INTO `Operator` VALUES (100000,'bj89ers','dev+bj01@ticketstar.jp',10,NULL,1,'2012-07-10 17:44:29','2012-07-10 17:44:29',NULL);
INSERT INTO `Operator` VALUES (100001,'bjnh','dev+bj02@ticketstar.jp',11,NULL,1,'2012-07-10 17:44:29','2012-07-10 17:44:29',NULL);

INSERT INTO `OperatorAuth` VALUES (100000,'dev+bj01@ticketstar.jp','21232f297a57a5a743894a0e4a801fc3','auth_code','access_token','secret_key','2012-07-10 17:44:29','2012-07-10 17:44:29');
INSERT INTO `OperatorAuth` VALUES (100001,'dev+bj02@ticketstar.jp','21232f297a57a5a743894a0e4a801fc3','auth_code','access_token','secret_key','2012-07-10 17:44:29','2012-07-10 17:44:29');

INSERT INTO `OperatorRole_Operator` VALUES (NULL,1,100000);
INSERT INTO `OperatorRole_Operator` VALUES (NULL,1,100001);

INSERT INTO `SalesSegment` VALUES (100000,'プラチナ会員用',NULL,'2012-07-01 00:00:00','2012-08-31 00:00:00',10000,0,100001,'2012-07-10 17:44:29','2012-07-10 17:44:29', NULL, 100002);

INSERT INTO `DeliveryMethod` VALUES (100000,'なし',0.00,0,10,1,'2012-07-10 17:44:29','2012-07-10 17:44:29',NULL);

INSERT INTO `PaymentMethod` VALUES (100000,'クレジットカード払い',0.00,0,10,1,'2012-07-10 17:44:29','2012-07-10 17:44:29',NULL);
INSERT INTO `PaymentMethod` VALUES (100001,'セブンイレブン支払い',158.00,0,10,3,'2012-07-10 17:44:29','2012-07-10 17:44:29',NULL);

INSERT INTO `PaymentDeliveryMethodPair` (id, system_fee, transaction_fee, delivery_fee, discount, discount_unit, sales_segment_id, payment_method_id, delivery_method_id, created_at, updated_at, deleted_at, payment_period_days, issuing_interval_days, issuing_start_at, issuing_end_at) VALUES (NULL,0.00,0.00,0.00,0.00,0,100000,100000,100000,'2012-07-10 17:44:29','2012-07-10 17:44:29',NULL,3,1,'2012-07-10 17:44:29','2012-07-10 17:44:29');
INSERT INTO `PaymentDeliveryMethodPair` (id, system_fee, transaction_fee, delivery_fee, discount, discount_unit, sales_segment_id, payment_method_id, delivery_method_id, created_at, updated_at, deleted_at, payment_period_days, issuing_interval_days, issuing_start_at, issuing_end_at) VALUES (NULL,0.00,158.00,0.00,0.00,0,100000,100001,100000,'2012-07-10 17:44:29','2012-07-10 17:44:29',NULL,3,1,'2012-07-10 17:44:29','2012-07-10 17:44:29');

INSERT INTO `Performance` VALUES (100000,'FC会員登録２０１２','B8REG2012000',NULL,NULL,NULL,100001,'2012-07-10 17:44:29','2012-07-10 17:44:29',NULL);
INSERT INTO `Site` (id) VALUES (100000);
INSERT INTO `Venue` (id, site_id, performance_id, organization_id, name, sub_name, original_venue_id, created_at, updated_at, deleted_at) 
VALUES (100000,100000,100000,10,'座席なし会場',NULL,NULL,'2012-06-20 12:09:33','2012-07-10 17:44:29',NULL);

INSERT INTO `Product` (id, name, price, sales_segment_id, event_id, created_at, updated_at, deleted_at) VALUES (100000,'法人会員',100500.00,100000,100001,'2012-07-10 17:44:29','2012-07-10 17:44:29',NULL);
INSERT INTO `Product` (id, name, price, sales_segment_id, event_id, created_at, updated_at, deleted_at) VALUES (100001,'プラチナ会員',30000.00,100000,100001,'2012-07-10 17:44:29','2012-07-10 17:44:29',NULL);
INSERT INTO `Product` (id, name, price, sales_segment_id, event_id, created_at, updated_at, deleted_at) VALUES (100002,'ゴールド会員',10000.00,100000,100001,'2012-07-10 17:44:29','2012-07-10 17:44:29',NULL);
INSERT INTO `Product` (id, name, price, sales_segment_id, event_id, created_at, updated_at, deleted_at) VALUES (100003,'レギュラー会員',3000.00,100000,100001,'2012-07-10 17:44:29','2012-07-10 17:44:29',NULL);
INSERT INTO `Product` (id, name, price, sales_segment_id, event_id, created_at, updated_at, deleted_at) VALUES (100004,'ライト会員',1000.00,100000,100001,'2012-07-10 17:44:29','2012-07-10 17:44:29',NULL);
INSERT INTO `Product` (id, name, price, sales_segment_id, event_id, created_at, updated_at, deleted_at) VALUES (100005,'ジュニア会員',1000.00,100000,100001,'2012-07-10 17:44:29','2012-07-10 17:44:29',NULL);

INSERT INTO `StockHolder` VALUES (100000,'89ers',100001,100000,'{\"text\": \"B\", \"text_color\": \"#ffd940\"}','2012-07-10 17:44:29','2012-07-11 05:34:38',NULL);

INSERT INTO `StockType` (id, name, `type`, event_id, quantity_only, style, created_at, updated_at, deleted_at) VALUES (100000,'89ERS会員権',1,NULL,1,'{}','2012-07-10 17:44:29','2012-07-10 17:44:29',NULL);
INSERT INTO `StockType` (id, name, `type`, event_id, quantity_only, style, created_at, updated_at, deleted_at) VALUES (100001,'Tシャツ',1,NULL,1,'{}','2012-07-10 17:44:29','2012-07-10 17:44:29',NULL);

INSERT INTO `Stock` VALUES (100000,1000,100000,100000,100000,'1000002-07-10 17:44:29','1000002-07-10 17:44:29',NULL);
INSERT INTO `Stock` VALUES (100001,1000,100000,100000,100001,'1000002-07-10 17:44:29','1000002-07-10 17:44:29',NULL);
INSERT INTO `StockStatus` (stock_id, quantity) VALUES (100000,1000);
INSERT INTO `StockStatus` (stock_id, quantity) VALUES (100001,1000);

INSERT INTO `ProductItem` (id, price, product_id, performance_id, stock_id, quantity, created_at, updated_at, deleted_at) VALUES (NULL,100500.00,100000,100000,100000,1,'2012-07-10 17:44:29','2012-07-11 05:35:33',NULL);
INSERT INTO `ProductItem` (id, price, product_id, performance_id, stock_id, quantity, created_at, updated_at, deleted_at) VALUES (NULL,0.00,100000,100000,100001,1,'2012-07-10 17:44:29','2012-07-11 05:35:42',NULL);
INSERT INTO `ProductItem` (id, price, product_id, performance_id, stock_id, quantity, created_at, updated_at, deleted_at) VALUES (NULL,30000.00,100001,100000,100000,1,'2012-07-10 17:44:29','2012-07-11 05:35:48',NULL);
INSERT INTO `ProductItem` (id, price, product_id, performance_id, stock_id, quantity, created_at, updated_at, deleted_at) VALUES (NULL,0.00,100001,100000,100001,1,'2012-07-10 17:44:29','2012-07-11 05:35:56',NULL);
INSERT INTO `ProductItem` (id, price, product_id, performance_id, stock_id, quantity, created_at, updated_at, deleted_at) VALUES (NULL,10000.00,100002,100000,100000,1,'2012-07-10 17:44:29','2012-07-11 05:36:04',NULL);
INSERT INTO `ProductItem` (id, price, product_id, performance_id, stock_id, quantity, created_at, updated_at, deleted_at) VALUES (NULL,0.00,100002,100000,100001,1,'2012-07-10 17:44:29','2012-07-11 05:36:11',NULL);
INSERT INTO `ProductItem` (id, price, product_id, performance_id, stock_id, quantity, created_at, updated_at, deleted_at) VALUES (NULL,3000.00,100003,100000,100000,1,'2012-07-10 17:44:29','2012-07-11 05:36:18',NULL);
INSERT INTO `ProductItem` (id, price, product_id, performance_id, stock_id, quantity, created_at, updated_at, deleted_at) VALUES (NULL,1000.00,100004,100000,100000,1,'2012-07-10 17:44:29','2012-07-11 05:36:28',NULL);
INSERT INTO `ProductItem` (id, price, product_id, performance_id, stock_id, quantity, created_at, updated_at, deleted_at) VALUES (NULL,1000.00,100005,100000,100000,1,'2012-07-10 17:44:29','2012-07-11 05:36:36',NULL);
COMMIT;
