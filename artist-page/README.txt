
Create database
---------------

$ echo 'create database artistpage charset=utf8;' | mysql -uroot 
$ cat sql/artistpage_dump.dat| mysql -uroot artistpage
$ cat sql/grant_database.sql | mysql -uroot artistpage 

Start Test Server
-----------------

$ LISTEN_PORT=8080 httpd -f ${PWD}/conf/http.conf

Kill Test server
----------------

# kill `cat /tmp/pid`
