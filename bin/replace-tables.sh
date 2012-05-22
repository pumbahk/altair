## drop
#echo  "drop database altaircms; create database altaircms default character set utf8; drop database ticketing; create database ticketing default character set utf8;" | mysql -u root -p
## create
pushd ../cms
python setup.py upgrade_db
pmain -c deploy/production.ini -s altaircms.scripts.pmain.insert_demodata
popd

pushd ../ticketing/src
python seed_import.py
popd
