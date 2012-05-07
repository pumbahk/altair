import commands

print commands.getstatusoutput('''echo 'drop database ticketing;' | mysql -u root''')
print commands.getstatusoutput('''echo 'create database ticketing charset=utf8;' | mysql -u root''')
print commands.getstatusoutput('''echo 'grant all on ticketing.* to ticketing@localhost identified by "ticketing";' | mysql -u root''')

import ticketing.seed.importer

print commands.getstatusoutput('''pmain  -c development.ini -s ticketing.scripts.pmain.seed_import''')

