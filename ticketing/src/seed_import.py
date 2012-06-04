import commands
import sqlalchemy
import sqlahelper
try:
    import pymysql_sa
    pymysql_sa.make_default_mysql_dialect()
    print 'Using PyMySQL'
except:
    pass
from ticketing.seed.importer import import_seed_data

print commands.getstatusoutput('''echo 'drop database ticketing;' | mysql -u root''')
print commands.getstatusoutput('''echo 'create database ticketing charset=utf8;' | mysql -u root''')
print commands.getstatusoutput('''echo 'grant all on ticketing.* to ticketing@localhost identified by "ticketing";' | mysql -u root''')


sqlahelper.add_engine(sqlalchemy.create_engine('mysql+pymysql://ticketing:ticketing@127.0.0.1/ticketing?use_unicode=true&charset=utf8', echo=True))

import_seed_data()

# print commands.getstatusoutput('''pmain  -c development.ini -s ticketing.scripts.pmain.seed_import''')

