/* For the loading from the result of select_seat_choice.bash */

drop table if exists order_select;
create table order_select (
    id int unsigned not null auto_increment,
    recorded_at datetime(3) not null,
    cart_xbi char(40) character set ascii not null default '',
    selector enum('system', 'user') not null,
    primary key (id),
    key (cart_xbi, recorded_at, selector)
) engine=innodb default charset=utf8;
load data local infile './order_select.out' into table order_select (recorded_at, cart_xbi, selector);
