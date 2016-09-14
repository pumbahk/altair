PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;

DROP TABLE IF EXISTS VisselMemberKind;
DROP TABLE IF EXISTS VisselMemberShip;
DROP TABLE IF EXISTS VisselUser;

CREATE TABLE "VisselMemberKind" (
id INTEGER NOT NULL,
name VARCHAR(255) NOT NULL,
PRIMARY KEY (id)
);
CREATE TABLE "VisselMembership" (
id INTEGER NOT NULL,
membership_id VARCHAR(32) NOT NULL,
user_id INTEGER NOT NULL,
kind_id INTEGER NOT NULL,
valid_since DATETIME,
expire_at DATETIME,
created_at DATETIME,
PRIMARY KEY (id),
FOREIGN KEY(user_id) REFERENCES "VisselUser" (id) ON DELETE CASCADE,
FOREIGN KEY(kind_id) REFERENCES "VisselMemberKind" (id) ON DELETE CASCADE
);
CREATE TABLE "VisselUser" (
id INTEGER NOT NULL,
name VARCHAR(255) NOT NULL,
member_no VARCHAR(255) NOT NULL,
openid_claimed_id VARCHAR(255),
related_at DATETIME,
created_at DATETIME,
PRIMARY KEY (id),
UNIQUE (openid_claimed_id)
);

INSERT INTO "VisselMemberKind" (id, name) VALUES (10001, 'レギュラークラブ');
INSERT INTO "VisselMemberKind" (id, name) VALUES (10002, 'キッズクラブ');
INSERT INTO "VisselUser" (id, name, openid_claimed_id, member_no) VALUES(0,'user00','https://myid.rakuten.co.jp/openid/user/75Gm1XuC3F3VWwRs1pN0IQ==', '0000-0000-0000-0000');
INSERT INTO "VisselUser" (id, name, openid_claimed_id, member_no) VALUES(1,'user01','https://myid.rakuten.co.jp/openid/user/7KtaSulpTdTCm6crf7iL20OzA==', '0000-0000-0000-0001');
INSERT INTO "VisselUser" (id, name, openid_claimed_id, member_no) VALUES(2,'user02','https://myid.rakuten.co.jp/openid/user/Hpv5eXl5JI8CrYM3P5yjcQ==', '0000-0000-0000-0002');
INSERT INTO "VisselUser" (id, name, openid_claimed_id, member_no) VALUES(3,'user03','https://myid.rakuten.co.jp/openid/user/bIMWmxINsJTVWwRs1pN0IQ==', '0000-0000-0000-0003');
INSERT INTO "VisselUser" (id, name, openid_claimed_id, member_no) VALUES(4,'user04','https://myid.rakuten.co.jp/openid/user/bIMWmxINsJRMhZac1O32cQ==', '0000-0000-0000-0004');
INSERT INTO "VisselUser" (id, name, openid_claimed_id, member_no) VALUES(5,'user05','https://myid.rakuten.co.jp/openid/user/Hpv5eXl5JISulpcrf7iL20OzA==', '0000-0000-0000-0005');
INSERT INTO "VisselUser" (id, name, openid_claimed_id, member_no) VALUES(6,'user06','https://myid.rakuten.co.jp/openid/user/BI9WNddV9dL4Drv1c2uMCg==', '0000-0000-0000-0006');
INSERT INTO "VisselUser" (id, name, openid_claimed_id, member_no) VALUES(7,'user07','https://myid.rakuten.co.jp/openid/user/BI9WNddV9dJVhV4SulpWCE9OA==', '0000-0000-0000-0007');
INSERT INTO "VisselUser" (id, name, openid_claimed_id, member_no) VALUES(8,'user08','https://myid.rakuten.co.jp/openid/user/BI9WNddV9dICrYM3P5yjcQ==', '0000-0000-0000-0008');
INSERT INTO "VisselUser" (id, name, openid_claimed_id, member_no) VALUES(9,'user09','https://myid.rakuten.co.jp/openid/user/8PhdFQSAVvoCrYM3P5yjcQ==', '0000-0000-0000-0009');
INSERT INTO "VisselUser" (id, name, openid_claimed_id, member_no) VALUES(10,'user10','https://myid.rakuten.co.jp/openid/user/BI9WNddV9dJMhZac1O32cQ==', '0000-0000-0000-0010');
INSERT INTO "VisselUser" (id, name, openid_claimed_id, member_no) VALUES(11,'user11','https://myid.rakuten.co.jp/openid/user/8PhdFQSAVvqcrf7iL20OzA==', '0000-0000-0000-0011');
INSERT INTO "VisselUser" (id, name, openid_claimed_id, member_no) VALUES(12,'user12','https://myid.rakuten.co.jp/openid/user/4HY4oMt6jZJVhV4SulpWCE9OA==', '0000-0000-0000-0012');
INSERT INTO "VisselUser" (id, name, openid_claimed_id, member_no) VALUES(13,'user13','https://myid.rakuten.co.jp/openid/user/BHsalsGheke6BBJVhV4SulpWCE9OA==', '0000-0000-0000-0013');
INSERT INTO "VisselUser" (id, name, openid_claimed_id, member_no) VALUES(14,'user14','https://myid.rakuten.co.jp/openid/user/uwffhrFDs6QGsmquSulpNtQKg==', '0000-0000-0000-0014');
INSERT INTO "VisselUser" (id, name, openid_claimed_id, member_no) VALUES(15,'user15','https://myid.rakuten.co.jp/openid/user/4HY4oMt6jZIGsmquSulpNtQKg==', '0000-0000-0000-0015');
INSERT INTO "VisselUser" (id, name, openid_claimed_id, member_no) VALUES(16,'user16','https://myid.rakuten.co.jp/openid/user/XxOOwBMiOr1MhZac1O32cQ==', '0000-0000-0000-0016');
INSERT INTO "VisselUser" (id, name, openid_claimed_id, member_no) VALUES(17,'user17','https://myid.rakuten.co.jp/openid/user/EGbFNtc5Ox9MhZac1O32cQ==', '0000-0000-0000-0017');
INSERT INTO "VisselUser" (id, name, openid_claimed_id, member_no) VALUES(18,'user18','https://myid.rakuten.co.jp/openid/user/xpTC9ILcoRNMhZac1O32cQ==', '0000-0000-0000-0018');
INSERT INTO "VisselUser" (id, name, openid_claimed_id, member_no) VALUES(19,'user19','https://myid.rakuten.co.jp/openid/user/SyaEcQgpyVDKS1ntSulpm4DBQ==', '0000-0000-0000-0019');
INSERT INTO "VisselUser" (id, name, openid_claimed_id, member_no) VALUES(20,'user20','https://myid.rakuten.co.jp/openid/user/z6O8bkFuSBkGsmquSulpNtQKg==', '0000-0000-0000-0020');
INSERT INTO "VisselMembership" (membership_id, user_id, kind_id, valid_since, expire_at) VALUES('0000-0000-0001-0000',1,10001,'2016-01-01 00:00:00.000000','2018-01-01 00:00:00.000000');
INSERT INTO "VisselMembership" (membership_id, user_id, kind_id, valid_since, expire_at) VALUES('0000-0000-0001-0100',2,10002,'2016-01-01 00:00:00.000000','2018-01-01 00:00:00.000000');
INSERT INTO "VisselMembership" (membership_id, user_id, kind_id, valid_since, expire_at) VALUES('0000-0000-0001-1800',18,10001,'2016-01-01 00:00:00.000000','2018-01-01 00:00:00.000000');
INSERT INTO "VisselMembership" (membership_id, user_id, kind_id, valid_since, expire_at) VALUES('0000-0000-0001-1801',18,10002,'2016-01-01 00:00:00.000000','2018-01-01 00:00:00.000000');
COMMIT;
