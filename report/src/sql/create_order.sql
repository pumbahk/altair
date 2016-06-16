/* To be created on report DB. Data is to be written by select_order.py */

drop table if exists order201605;
create table order201605 (
    id int unsigned not null auto_increment,
    event_id int unsigned not null,
    event_name varchar(1023) not null,
    perf_id int unsigned not null,
    perf_name varchar(1023) not null,
    start_on date not null,
    cart_id int unsigned not null,
    order_id int unsigned not null,
    channel tinyint unsigned not null,
    order_no char(12) character set ascii not null,
    cart_xbi char(40) character set ascii not null default '',
    order_xbi char(40) character set ascii not null default '',
    carted_at datetime not null,
    ordered_at datetime not null,
    -- select_type enum('user', 'system', 'unknown') not null default 'unknown', # For seat choice type
    ua_type enum('atab', 'asp', 'itab', 'isp', 'sp', 'fp', 'pc') not null,
    order_status enum('ordered', 'canceled', 'delivered') not null,
    payment_status enum('paid', 'unpaid', 'refunded', 'refunding') not null,
    delivery_status enum('delivered', 'undelivered') not null,
    payment_method tinyint not null,
    delivery_method tinyint not null,
    fc_type varchar(1023) not null,
    fc_id varchar(1023) not null,
    total int unsigned not null,
    fee int unsigned not null,
    qty int unsigned not null,
    point int unsigned not null,
    primary key (id),
    key (order_id),
    key (order_no)
) engine=innodb default charset=utf8;