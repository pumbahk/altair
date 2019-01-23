README
-----------

Setup
=====
::

ローカルに開発環境を作成する方法
====================================
1.DBを作成する
====================================

`mysql -u root
CREATE DATABASE `newsletter` DEFAULT CHARSET utf8;
GRANT ALL ON `newsletter`.* TO `newsletter`@'127.0.0.1' IDENTIFIED BY 'newsletter';
GRANT ALL ON `newsletter`.* TO `newsletter`@'localhost' IDENTIFIED BY 'newsletter';
create user 'newsletter'@'localhost' identified by 'newsletter';

use newsletter;

CREATE TABLE `Newsletter` (
`id` bigint(20) NOT NULL AUTO_INCREMENT,
`subject` varchar(255) DEFAULT NULL,
`description` text,
`type` varchar(255) DEFAULT NULL,
`status` varchar(255) DEFAULT NULL,
`sender_address` varchar(255) DEFAULT NULL,
`sender_name` varchar(255) DEFAULT NULL,
`subscriber_count` bigint(20) DEFAULT NULL,
`start_on` datetime DEFAULT NULL,
`created_at` datetime DEFAULT NULL,
`updated_at` datetime DEFAULT NULL,
PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1107 DEFAULT CHARSET=utf8;
`


2.supervisorctlで立ち上げる
====================================
`./altair/deploy/dev/bin/supervisorctl start altair.newsletter.admin`

Useful Resources
================

* `Pyramid Documentation <http://docs.pylonsproject.org/docs/pyramid.html>`_
* `Pyramid Migration Guide <http://bytebucket.org/sluggo/pyramid-docs/wiki/html/migration.html>`_
