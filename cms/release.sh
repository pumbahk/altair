mysql -u root -p root <<EOF
drop database altaircms;
create database altaircms default character set utf8;
EOF
mysql -u root -p altaircms < 
