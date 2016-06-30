/* To be created on report DB. Data is to be writen by select_item.py */

drop table if exists order_seat201605;
create table order_seat201605 (
    id int unsigned not null auto_increment,
    order_id int unsigned not null,
    item_id int unsigned not null,
    item_serial int unsigned not null,
    item_name varchar(1023) not null,
    item_price int unsigned not null,
    seat_name varchar(1023) not null,
    primary key (id),
    key (order_id)
) engine=innodb default charset=utf8;