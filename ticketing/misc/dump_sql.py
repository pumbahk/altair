import re
import sys
import json
import datetime

class Decimal(object):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value

def escape(ustr):
    return ustr.replace("'", "''")

def format(fields):
    for field in fields:
        if isinstance(field, str):
            yield u"'%s'" % escape(field.decode('utf-8'))
        elif isinstance(field, unicode):
            yield u"'%s'" % escape(field)
        elif isinstance(field, datetime.datetime):
            yield u"'%s'" % field.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(field, datetime.date):
            yield u"'%s'" % field.strftime("%Y-%m-%d")
        elif field is None:
            yield u"NULL"
        else:
            yield unicode(field) 

prev_sql = None
sql = None
buf = ''
placeholders = []
date = None

for line in sys.stdin:
    json_str = line.rstrip().split('\t')[2]
    entry = json.loads(json_str)
    if entry['sys_name'] == 'sqlalchemy.engine.base.Engine':
        _ = entry['message'].split(' ', 7)[-1]
        prev_sql = sql
        sql = _
        if prev_sql == sql:
            continue
        if sql[0] == u'(':
            placeholders += list(eval(sql))
            try:
                print '--', date
                print (buf % tuple(format(placeholders))).rstrip().encode('utf-8') + ';\n'
                buf = ''
                placeholders = []
                date = None
            except TypeError:
                pass
        else:
            if date is None:
                date = entry['time']
            buf += sql + u'\n'

# vim: sts=4 sw=4 ts=4 et
