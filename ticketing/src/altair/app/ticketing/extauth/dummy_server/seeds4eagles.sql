PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;

DROP TABLE IF EXISTS EaglesMemberKind;
DROP TABLE IF EXISTS EaglesMemberShip;
DROP TABLE IF EXISTS EaglesCoupon;
DROP TABLE IF EXISTS EaglesUser;

CREATE TABLE "EaglesMemberKind" (
id INTEGER NOT NULL,
name VARCHAR(255) NOT NULL,
PRIMARY KEY (id)
);
CREATE TABLE "EaglesMembership" (
id INTEGER NOT NULL,
membership_id VARCHAR(32) NOT NULL,
user_id INTEGER NOT NULL,
kind_id INTEGER NOT NULL,
valid_since DATETIME,
expire_at DATETIME,
created_at DATETIME,
PRIMARY KEY (id),
FOREIGN KEY(user_id) REFERENCES "EaglesUser" (id) ON DELETE CASCADE,
FOREIGN KEY(kind_id) REFERENCES "EaglesMemberKind" (id) ON DELETE CASCADE
);
CREATE TABLE "EaglesCoupon" (
id INTEGER NOT NULL,
user_id INTEGER NOT NULL,
code VARCHAR(12) NOT NULL,
name VARCHAR(255) NOT NULL,
available_flg NUMERIC(1) NOT NULL,
PRIMARY KEY (id),
FOREIGN KEY(user_id) REFERENCES "EaglesUser" (id) ON DELETE CASCADE,
UNIQUE (code)
);
CREATE TABLE "EaglesUser" (
id INTEGER NOT NULL,
name VARCHAR(255) NOT NULL,
member_no VARCHAR(255) NOT NULL,
openid_claimed_id VARCHAR(255),
related_at DATETIME,
created_at DATETIME,
PRIMARY KEY (id),
UNIQUE (openid_claimed_id)
);

INSERT INTO "EaglesMemberKind" (id, name) VALUES (10001, 'ブースタークラブ');
INSERT INTO "EaglesMemberKind" (id, name) VALUES (10002, 'ゴールドクラブ');
INSERT INTO "EaglesMemberKind" (id, name) VALUES (10003, 'レギュラークラブ');
INSERT INTO "EaglesMemberKind" (id, name) VALUES (10004, 'E25クラブ');
INSERT INTO "EaglesMemberKind" (id, name) VALUES (10005, 'レディースクラブ');
INSERT INTO "EaglesMemberKind" (id, name) VALUES (10006, 'スポンサークラブ');
INSERT INTO "EaglesMemberKind" (id, name) VALUES (10007, 'キッズクラブ');
INSERT INTO "EaglesMemberKind" (id, name) VALUES (10008, 'ベーシッククラブ');
INSERT INTO "EaglesMemberKind" (id, name) VALUES (10009, 'TSC');
INSERT INTO "EaglesMemberKind" (id, name) VALUES (10010, 'チーム青森');
INSERT INTO "EaglesMemberKind" (id, name) VALUES (10011, 'チーム秋田');
INSERT INTO "EaglesMemberKind" (id, name) VALUES (10012, 'チーム岩手');
INSERT INTO "EaglesMemberKind" (id, name) VALUES (10013, 'チーム宮城');
INSERT INTO "EaglesMemberKind" (id, name) VALUES (10014, 'チーム山形');
INSERT INTO "EaglesMemberKind" (id, name) VALUES (10015, 'チーム福島');
INSERT INTO "EaglesMemberKind" (id, name) VALUES (10016, 'スクールFC');
INSERT INTO "EaglesMemberKind" (id, name) VALUES (10017, 'スタメン');
INSERT INTO "EaglesUser" (id, name, openid_claimed_id, member_no) VALUES(0,'user00','https://myid.rakuten.co.jp/openid/user/75Gm1XuC3F3VWwRs1pN0IQ==', '0000-0000-0000-0000');
INSERT INTO "EaglesUser" (id, name, openid_claimed_id, member_no) VALUES(1,'user01','https://myid.rakuten.co.jp/openid/user/7KtaSulpTdTCm6crf7iL20OzA==', '0000-0000-0000-0001'); -- ログインID:　tickettestusers+1 パスワード: rakuten
INSERT INTO "EaglesUser" (id, name, openid_claimed_id, member_no) VALUES(2,'user02','https://myid.rakuten.co.jp/openid/user/Hpv5eXl5JI8CrYM3P5yjcQ==', '0000-0000-0000-0002');
INSERT INTO "EaglesUser" (id, name, openid_claimed_id, member_no) VALUES(3,'user03','https://myid.rakuten.co.jp/openid/user/bIMWmxINsJTVWwRs1pN0IQ==', '0000-0000-0000-0003');
INSERT INTO "EaglesUser" (id, name, openid_claimed_id, member_no) VALUES(4,'user04','https://myid.rakuten.co.jp/openid/user/bIMWmxINsJRMhZac1O32cQ==', '0000-0000-0000-0004');
INSERT INTO "EaglesUser" (id, name, openid_claimed_id, member_no) VALUES(5,'user05','https://myid.rakuten.co.jp/openid/user/Hpv5eXl5JISulpcrf7iL20OzA==', '0000-0000-0000-0005');
INSERT INTO "EaglesUser" (id, name, openid_claimed_id, member_no) VALUES(6,'user06','https://myid.rakuten.co.jp/openid/user/BI9WNddV9dL4Drv1c2uMCg==', '0000-0000-0000-0006');
INSERT INTO "EaglesUser" (id, name, openid_claimed_id, member_no) VALUES(7,'user07','https://myid.rakuten.co.jp/openid/user/BI9WNddV9dJVhV4SulpWCE9OA==', '0000-0000-0000-0007');
INSERT INTO "EaglesUser" (id, name, openid_claimed_id, member_no) VALUES(8,'user08','https://myid.rakuten.co.jp/openid/user/BI9WNddV9dICrYM3P5yjcQ==', '0000-0000-0000-0008');
INSERT INTO "EaglesUser" (id, name, openid_claimed_id, member_no) VALUES(9,'user09','https://myid.rakuten.co.jp/openid/user/8PhdFQSAVvoCrYM3P5yjcQ==', '0000-0000-0000-0009');
INSERT INTO "EaglesUser" (id, name, openid_claimed_id, member_no) VALUES(10,'user10','https://myid.rakuten.co.jp/openid/user/BI9WNddV9dJMhZac1O32cQ==', '0000-0000-0000-0010');
INSERT INTO "EaglesUser" (id, name, openid_claimed_id, member_no) VALUES(11,'user11','https://myid.rakuten.co.jp/openid/user/8PhdFQSAVvqcrf7iL20OzA==', '0000-0000-0000-0011');
INSERT INTO "EaglesUser" (id, name, openid_claimed_id, member_no) VALUES(12,'user12','https://myid.rakuten.co.jp/openid/user/4HY4oMt6jZJVhV4SulpWCE9OA==', '0000-0000-0000-0012');
INSERT INTO "EaglesUser" (id, name, openid_claimed_id, member_no) VALUES(13,'user13','https://myid.rakuten.co.jp/openid/user/BHsalsGheke6BBJVhV4SulpWCE9OA==', '0000-0000-0000-0013');
INSERT INTO "EaglesUser" (id, name, openid_claimed_id, member_no) VALUES(14,'user14','https://myid.rakuten.co.jp/openid/user/uwffhrFDs6QGsmquSulpNtQKg==', '0000-0000-0000-0014');
INSERT INTO "EaglesUser" (id, name, openid_claimed_id, member_no) VALUES(15,'user15','https://myid.rakuten.co.jp/openid/user/4HY4oMt6jZIGsmquSulpNtQKg==', '0000-0000-0000-0015');
INSERT INTO "EaglesUser" (id, name, openid_claimed_id, member_no) VALUES(16,'user16','https://myid.rakuten.co.jp/openid/user/XxOOwBMiOr1MhZac1O32cQ==', '0000-0000-0000-0016');
INSERT INTO "EaglesUser" (id, name, openid_claimed_id, member_no) VALUES(17,'user17','https://myid.rakuten.co.jp/openid/user/EGbFNtc5Ox9MhZac1O32cQ==', '0000-0000-0000-0017');
INSERT INTO "EaglesUser" (id, name, openid_claimed_id, member_no) VALUES(18,'user18','https://myid.rakuten.co.jp/openid/user/xpTC9ILcoRNMhZac1O32cQ==', '0000-0000-0000-0018');
INSERT INTO "EaglesUser" (id, name, openid_claimed_id, member_no) VALUES(19,'user19','https://myid.rakuten.co.jp/openid/user/SyaEcQgpyVDKS1ntSulpm4DBQ==', '0000-0000-0000-0019');
INSERT INTO "EaglesUser" (id, name, openid_claimed_id, member_no) VALUES(20,'user20','https://myid.rakuten.co.jp/openid/user/z6O8bkFuSBkGsmquSulpNtQKg==', '0000-0000-0000-0020');
INSERT INTO "EaglesMembership" (membership_id, user_id, kind_id, valid_since, expire_at) VALUES('0000001',0,10001,'2015-01-01 00:00:00.000000','2017-01-01 00:00:00.000000');
INSERT INTO "EaglesMembership" (membership_id, user_id, kind_id, valid_since, expire_at) VALUES('0000002',1,10001,'2015-01-01 00:00:00.000000','2017-01-01 00:00:00.000000');
INSERT INTO "EaglesMembership" (membership_id, user_id, kind_id, valid_since, expire_at) VALUES('0000003',2,10002,'2015-01-01 00:00:00.000000','2017-01-01 00:00:00.000000');
INSERT INTO "EaglesMembership" (membership_id, user_id, kind_id, valid_since, expire_at) VALUES('0000004',3,10003,'2015-01-01 00:00:00.000000','2017-01-01 00:00:00.000000');
INSERT INTO "EaglesMembership" (membership_id, user_id, kind_id, valid_since, expire_at) VALUES('0000005',4,10005,'2015-01-01 00:00:00.000000','2017-01-01 00:00:00.000000');
INSERT INTO "EaglesMembership" (membership_id, user_id, kind_id, valid_since, expire_at) VALUES('0000006',5,10007,'2015-01-01 00:00:00.000000','2017-01-01 00:00:00.000000');
INSERT INTO "EaglesMembership" (membership_id, user_id, kind_id, valid_since, expire_at) VALUES('0000007',6,10004,'2015-01-01 00:00:00.000000','2017-01-01 00:00:00.000000');
INSERT INTO "EaglesMembership" (membership_id, user_id, kind_id, valid_since, expire_at) VALUES('0000008',7,10008,'2015-01-01 00:00:00.000000','2017-01-01 00:00:00.000000');
INSERT INTO "EaglesMembership" (membership_id, user_id, kind_id, valid_since, expire_at) VALUES('0000009',8,10006,'2015-01-01 00:00:00.000000','2017-01-01 00:00:00.000000');
INSERT INTO "EaglesMembership" (membership_id, user_id, kind_id, valid_since, expire_at) VALUES('0000010',9,10009,'2015-01-01 00:00:00.000000','2017-01-01 00:00:00.000000');
INSERT INTO "EaglesMembership" (membership_id, user_id, kind_id, valid_since, expire_at) VALUES('0000011',10,10017,'2015-01-01 00:00:00.000000','2017-01-01 00:00:00.000000');
INSERT INTO "EaglesMembership" (membership_id, user_id, kind_id, valid_since, expire_at) VALUES('0000012',11,10016,'2015-01-01 00:00:00.000000','2017-01-01 00:00:00.000000');
INSERT INTO "EaglesMembership" (membership_id, user_id, kind_id, valid_since, expire_at) VALUES('0000013',12,10010,'2015-01-01 00:00:00.000000','2017-01-01 00:00:00.000000');
INSERT INTO "EaglesMembership" (membership_id, user_id, kind_id, valid_since, expire_at) VALUES('0000014',13,10011,'2015-01-01 00:00:00.000000','2017-01-01 00:00:00.000000');
INSERT INTO "EaglesMembership" (membership_id, user_id, kind_id, valid_since, expire_at) VALUES('0000015',14,10012,'2015-01-01 00:00:00.000000','2017-01-01 00:00:00.000000');
INSERT INTO "EaglesMembership" (membership_id, user_id, kind_id, valid_since, expire_at) VALUES('0000016',15,10013,'2015-01-01 00:00:00.000000','2017-01-01 00:00:00.000000');
INSERT INTO "EaglesMembership" (membership_id, user_id, kind_id, valid_since, expire_at) VALUES('0000017',16,10014,'2015-01-01 00:00:00.000000','2017-01-01 00:00:00.000000');
INSERT INTO "EaglesMembership" (membership_id, user_id, kind_id, valid_since, expire_at) VALUES('0000018',17,10015,'2015-01-01 00:00:00.000000','2017-01-01 00:00:00.000000');
INSERT INTO "EaglesMembership" (membership_id, user_id, kind_id, valid_since, expire_at) VALUES('0000019',18,10001,'2015-01-01 00:00:00.000000','2017-01-01 00:00:00.000000');
INSERT INTO "EaglesMembership" (membership_id, user_id, kind_id, valid_since, expire_at) VALUES('0000020',18,10002,'2015-01-01 00:00:00.000000','2017-01-01 00:00:00.000000');
INSERT INTO "EaglesMembership" (membership_id, user_id, kind_id, valid_since, expire_at) VALUES('0000021',18,10003,'2015-01-01 00:00:00.000000','2017-01-01 00:00:00.000000');
INSERT INTO "EaglesMembership" (membership_id, user_id, kind_id, valid_since, expire_at) VALUES('0000022',18,10005,'2015-01-01 00:00:00.000000','2017-01-01 00:00:00.000000');
INSERT INTO "EaglesMembership" (membership_id, user_id, kind_id, valid_since, expire_at) VALUES('0000023',18,10007,'2015-01-01 00:00:00.000000','2017-01-01 00:00:00.000000');
INSERT INTO "EaglesMembership" (membership_id, user_id, kind_id, valid_since, expire_at) VALUES('0000024',18,10004,'2015-01-01 00:00:00.000000','2017-01-01 00:00:00.000000');
INSERT INTO "EaglesMembership" (membership_id, user_id, kind_id, valid_since, expire_at) VALUES('0000025',18,10008,'2015-01-01 00:00:00.000000','2017-01-01 00:00:00.000000');
INSERT INTO "EaglesMembership" (membership_id, user_id, kind_id, valid_since, expire_at) VALUES('0000026',18,10006,'2015-01-01 00:00:00.000000','2017-01-01 00:00:00.000000');
INSERT INTO "EaglesMembership" (membership_id, user_id, kind_id, valid_since, expire_at) VALUES('0000027',18,10009,'2015-01-01 00:00:00.000000','2017-01-01 00:00:00.000000');
INSERT INTO "EaglesMembership" (membership_id, user_id, kind_id, valid_since, expire_at) VALUES('0000028',18,10017,'2015-01-01 00:00:00.000000','2017-01-01 00:00:00.000000');
INSERT INTO "EaglesMembership" (membership_id, user_id, kind_id, valid_since, expire_at) VALUES('0000029',18,10016,'2015-01-01 00:00:00.000000','2017-01-01 00:00:00.000000');
INSERT INTO "EaglesMembership" (membership_id, user_id, kind_id, valid_since, expire_at) VALUES('0000030',18,10010,'2015-01-01 00:00:00.000000','2017-01-01 00:00:00.000000');
INSERT INTO "EaglesMembership" (membership_id, user_id, kind_id, valid_since, expire_at) VALUES('0000031',18,10011,'2015-01-01 00:00:00.000000','2017-01-01 00:00:00.000000');
INSERT INTO "EaglesMembership" (membership_id, user_id, kind_id, valid_since, expire_at) VALUES('0000032',18,10012,'2015-01-01 00:00:00.000000','2017-01-01 00:00:00.000000');
INSERT INTO "EaglesMembership" (membership_id, user_id, kind_id, valid_since, expire_at) VALUES('0000033',18,10013,'2015-01-01 00:00:00.000000','2017-01-01 00:00:00.000000');
INSERT INTO "EaglesMembership" (membership_id, user_id, kind_id, valid_since, expire_at) VALUES('0000034',18,10014,'2015-01-01 00:00:00.000000','2017-01-01 00:00:00.000000');
INSERT INTO "EaglesMembership" (membership_id, user_id, kind_id, valid_since, expire_at) VALUES('0000035',18,10015,'2015-01-01 00:00:00.000000','2017-01-01 00:00:00.000000');
INSERT INTO "EaglesMembership" (membership_id, user_id, kind_id, valid_since, expire_at) VALUES('0000036',19,10001,'2015-01-01 00:00:00.000000','2017-01-01 00:00:00.000000');
INSERT INTO "EaglesMembership" (membership_id, user_id, kind_id, valid_since, expire_at) VALUES('0000037',19,10001,'2015-01-01 00:00:00.000000','2017-01-01 00:00:00.000000');
INSERT INTO "EaglesMembership" (membership_id, user_id, kind_id, valid_since, expire_at) VALUES('0000038',20,10002,'2015-01-01 00:00:00.000000','2017-01-01 00:00:00.000000');
INSERT INTO "EaglesMembership" (membership_id, user_id, kind_id, valid_since, expire_at) VALUES('0000039',20,10003,'2015-01-01 00:00:00.000000','2017-01-01 00:00:00.000000');
INSERT INTO "EaglesCoupon" (user_id, code, name, available_flg) VALUES(1, 'EEQT00000001', 'ダミークーポン01', 1);
INSERT INTO "EaglesCoupon" (user_id, code, name, available_flg) VALUES(1, 'EEQT00000002', 'ダミークーポン01', 1);
INSERT INTO "EaglesCoupon" (user_id, code, name, available_flg) VALUES(1, 'EEQT00000003', 'ダミークーポン01', 0);
INSERT INTO "EaglesCoupon" (user_id, code, name, available_flg) VALUES(2, 'EEQT00000004', 'ダミークーポン01', 1);
INSERT INTO "EaglesCoupon" (user_id, code, name, available_flg) VALUES(2, 'EEQT00000005', 'ダミークーポン01', 1);
INSERT INTO "EaglesCoupon" (user_id, code, name, available_flg) VALUES(2, 'EEQT00000006', 'ダミークーポン01', 0);
UPDATE EaglesMembership set expire_at = '2030-01-01 00:00:00.000000';
COMMIT;
