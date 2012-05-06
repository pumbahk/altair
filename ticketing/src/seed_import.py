import commands

print commands.getstatusoutput('''echo 'drop database ticketing;' | mysql -u root''')
print commands.getstatusoutput('''echo 'create database ticketing charset=utf8;' | mysql -u root''')
print commands.getstatusoutput('''echo 'grant all on ticketing.* to ticketing@localhost identified by "ticketing";' | mysql -u root''')

import seed.importer
