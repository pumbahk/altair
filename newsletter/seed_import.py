import commands

print commands.getstatusoutput('''echo 'drop database newsletter;' | mysql -u newsletter --password='newsletter' ''')
print commands.getstatusoutput('''echo 'create database newsletter charset=utf8;' | mysql -u newsletter --password='newsletter' ''')
print commands.getstatusoutput('''echo 'grant all on newsletter.* to newsletter@localhost identified by "newsletter";' | mysql -u root --password='' ''')

import seed
