import sqlalchemy
import sqlahelper
from paste.deploy.loadwsgi import appconfig
import argparse

from ticketing.oauth2.models import *
from ticketing.master.models import *
from ticketing.operators.models import *
from ticketing.orders.models import *
from ticketing.users.models import *
from ticketing.core.models import *
from ticketing.sej.models import *
from ticketing.bookmark.models import *
from ticketing.cart.models import *
from ticketing.multicheckout.models import *
from inspect import getfile, currentframe
import os
import re

def readsql(conn, f):
    buf = ''
    state = 0
    while True:
        chunk = f.read(4096)
        if not chunk:
            break
        e = -1
        for m in re.finditer(r"(['`;])", chunk):
            s = m.span()
            c = m.group(0)
            if state == 0:
                if c == "'":
                    state = 1
                elif c == '`':
                    state = 2
                elif c == ';':
                    e = s[0]
                    break
            elif state == 1:
                if c == "'":
                    if len(buf) <= s[0] + 1 or buf[s[0] + 1] != "'":
                        state = 0
            elif state == 2:
                if c == '`':
                    if len(buf) <= s[0] + 1 or buf[s[0] + 1] != '`':
                        state = 0
        if state != 0 or e < 0:
            buf += chunk
            continue
        sql = buf + chunk[0:e + 1]
        buf = chunk[e + 1:]
        conn.execute(sql) 

parser = argparse.ArgumentParser()
parser.add_argument('config', type=str, help='configuration file')
parser.add_argument('-d', nargs=1, type=str, metavar='param=value', action='append', help='extra settings')

args = parser.parse_args()

settings = appconfig('config:' + os.path.abspath(args.config))

if args.d is not None:
    for pair,  in args.d:
        k, v = pair.split('=')
        settings[k] = v

sqlahelper.add_engine(sqlalchemy.engine_from_config(settings, 'sqlalchemy.'))
sqlahelper.get_base().metadata.drop_all()
sqlahelper.get_base().metadata.create_all()

conn = sqlahelper.get_engine().connect()
f = open(os.path.dirname(getfile(currentframe())) + '/ticketing.sql')
readsql(conn, f)
