import commands
print "test"
print commands.getstatusoutput('''echo 'drop database ticketing;' | mysql -u ticketing --password='ticketing' ''')
print commands.getstatusoutput('''echo 'create database ticketing charset=utf8;' | mysql -u ticketing --password='ticketing' ''')
print commands.getstatusoutput('''echo 'grant all on ticketing.* to ticketing@localhost identified by "ticketing";' | mysql -u root --password='' ''')


import seed