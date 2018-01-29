PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;

INSERT INTO "VisselMemberKind" (id, name) VALUES (10001, 'レギュラークラブ');
INSERT INTO "VisselMemberKind" (id, name) VALUES (10002, 'キッズクラブ');
INSERT INTO "VisselUser" (id, name, openid_claimed_id, member_no) VALUES(21,'user21','https://myid.rakuten.co.jp/openid/user/rNmPCzshCVbzC2SulpKTnGlWg==', '0000-0000-0000-0021');
INSERT INTO "VisselUser" (id, name, openid_claimed_id, member_no) VALUES(22,'user22','https://myid.rakuten.co.jp/openid/user/7HsalsxKa7xcxHTzC2SulpKTnGlWg==', '0000-0000-0000-0022');
INSERT INTO "VisselUser" (id, name, openid_claimed_id, member_no) VALUES(23,'user23','https://myid.rakuten.co.jp/openid/user/XTcvMEutEKrzC2SulpKTnGlWg==', '0000-0000-0000-0023');
INSERT INTO "VisselMembership" (membership_id, user_id, kind_id, valid_since, expire_at) VALUES('0000-0000-0001-2100',21,10001,'2016-01-01 00:00:00.000000','2018-01-01 00:00:00.000000');
INSERT INTO "VisselMembership" (membership_id, user_id, kind_id, valid_since, expire_at) VALUES('0000-0000-0001-2200',22,10002,'2016-01-01 00:00:00.000000','2018-01-01 00:00:00.000000');
INSERT INTO "VisselMembership" (membership_id, user_id, kind_id, valid_since, expire_at) VALUES('0000-0000-0001-2300',23,10001,'2016-01-01 00:00:00.000000','2018-01-01 00:00:00.000000');
INSERT INTO "VisselMembership" (membership_id, user_id, kind_id, valid_since, expire_at) VALUES('0000-0000-0001-2301',23,10002,'2016-01-01 00:00:00.000000','2018-01-01 00:00:00.000000');
COMMIT;
