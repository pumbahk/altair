テストデータのseeding
---------------------

これが必要::

    mysql> INSERT INTO FamiPortPlayguide (name, discrimination_code) VALUES ('test', 1);
    Query OK, 1 row affected (0.01 sec)
    
    mysql> INSERT INTO FamiPortClient (famiport_playguide_id, code) VALUES (1, '000000000000000000000000');
    Query OK, 1 row affected, 1 warning (0.01 sec)
    
    mysql> INSERT INTO FamiPortTenant (organization_id, code) VALUES (15, '000000000000000000000000');
    Query OK, 1 row affected, 1 warning (0.01 sec)
    

あと、Altair側のEvent, Performance, SalesSegmentに対応する形でFamiPortEvent, FamiPortPerformance, FamiPortSalesSegmentへの値の追加が必要。

以下は例::

    mysql> DESC FamiPortEvent;
    +-------------------------+--------------+------+-----+---------------------+----------------+
    | Field                   | Type         | Null | Key | Default             | Extra          |
    +-------------------------+--------------+------+-----+---------------------+----------------+
    | id                      | bigint(20)   | NO   | PRI | NULL                | auto_increment |
    | userside_id             | bigint(20)   | YES  | MUL | NULL                |                |
    | code_1                  | varchar(6)   | NO   |     | NULL                |                |
    | code_2                  | varchar(4)   | NO   |     | NULL                |                |
    | name_1                  | varchar(80)  | NO   |     | NULL                |                |
    | name_2                  | varchar(80)  | NO   |     | NULL                |                |
    | sales_channel           | int(11)      | NO   |     | NULL                |                |
    | client_code             | varchar(24)  | YES  | MUL | NULL                |                |
    | venue_id                | bigint(20)   | YES  | MUL | NULL                |                |
    | purchasable_prefectures | varchar(137) | YES  |     | NULL                |                |
    | start_at                | datetime     | YES  |     | NULL                |                |
    | end_at                  | datetime     | YES  |     | NULL                |                |
    | genre_1_code            | varchar(23)  | YES  | MUL | NULL                |                |
    | genre_2_code            | varchar(35)  | YES  | MUL | NULL                |                |
    | keywords                | text         | YES  |     | NULL                |                |
    | search_code             | varchar(20)  | YES  |     | NULL                |                |
    | created_at              | timestamp    | NO   |     | CURRENT_TIMESTAMP   |                |
    | updated_at              | timestamp    | NO   |     | 0000-00-00 00:00:00 |                |
    +-------------------------+--------------+------+-----+---------------------+----------------+
    18 rows in set (0.00 sec)
    
    mysql> INSERT INTO FamiPortEvent (userside_id, code_1, code_2, name_1, name_2, client_code) VALUES (4382, 'RTFAMR', 'RTFM', 'ファミマ！！！', '', '000000000000000000000000');
    Query OK, 1 row affected, 1 warning (0.01 sec)
    
    mysql> SELECT LAST_INSERT_ID();
    +------------------+
    | LAST_INSERT_ID() |
    +------------------+
    |                1 |
    +------------------+
    1 row in set (0.01 sec)
    
    mysql> DESC FamiPortPerformance;
    +-------------------+-------------+------+-----+---------------------+----------------+
    | Field             | Type        | Null | Key | Default             | Extra          |
    +-------------------+-------------+------+-----+---------------------+----------------+
    | id                | bigint(20)  | NO   | PRI | NULL                | auto_increment |
    | userside_id       | bigint(20)  | YES  | MUL | NULL                |                |
    | famiport_event_id | bigint(20)  | NO   | MUL | NULL                |                |
    | code              | varchar(3)  | YES  |     | NULL                |                |
    | name              | varchar(60) | YES  |     | NULL                |                |
    | type              | int(11)     | NO   |     | NULL                |                |
    | searchable        | tinyint(1)  | NO   |     | NULL                |                |
    | sales_channel     | int(11)     | NO   |     | NULL                |                |
    | start_at          | datetime    | YES  |     | NULL                |                |
    | ticket_name       | varchar(20) | YES  |     | NULL                |                |
    | created_at        | timestamp   | NO   |     | CURRENT_TIMESTAMP   |                |
    | updated_at        | timestamp   | NO   |     | 0000-00-00 00:00:00 |                |
    +-------------------+-------------+------+-----+---------------------+----------------+
    12 rows in set (0.01 sec)
    
    mysql> INSERT INTO FamiPortPerformance (userside_id, famiport_event_id, code, name) VALUES (19603, 1, 'FFF', 'テスト');
    Query OK, 1 row affected, 3 warnings (0.02 sec)
    
    mysql> SELECT LAST_INSERT_ID();
    +------------------+
    | LAST_INSERT_ID() |
    +------------------+
    |                1 |
    +------------------+
    1 row in set (0.01 sec)
    
    mysql> DESC FamiPortSalesSegment;
    +-------------------------+--------------+------+-----+---------------------+----------------+
    | Field                   | Type         | Null | Key | Default             | Extra          |
    +-------------------------+--------------+------+-----+---------------------+----------------+
    | id                      | bigint(20)   | NO   | PRI | NULL                | auto_increment |
    | userside_id             | bigint(20)   | YES  | MUL | NULL                |                |
    | famiport_performance_id | bigint(20)   | NO   | MUL | NULL                |                |
    | code                    | varchar(3)   | NO   |     | NULL                |                |
    | name                    | varchar(40)  | NO   |     | NULL                |                |
    | sales_channel           | int(11)      | NO   |     | NULL                |                |
    | published_at            | datetime     | YES  |     | NULL                |                |
    | start_at                | datetime     | NO   |     | NULL                |                |
    | end_at                  | datetime     | YES  |     | NULL                |                |
    | auth_required           | tinyint(1)   | NO   |     | NULL                |                |
    | auth_message            | varchar(320) | NO   |     | NULL                |                |
    | seat_selection_start_at | datetime     | YES  |     | NULL                |                |
    | created_at              | timestamp    | NO   |     | CURRENT_TIMESTAMP   |                |
    | updated_at              | timestamp    | NO   |     | 0000-00-00 00:00:00 |                |
    +-------------------------+--------------+------+-----+---------------------+----------------+
    14 rows in set (0.01 sec)
    
    mysql> INSERT INTO FamiPortSalesSegment (userside_id, famiport_performance_id, code, name) VALUES (63750, 1, 'XXX', '一般販売');
    Query OK, 1 row affected, 4 warnings (0.01 sec)
