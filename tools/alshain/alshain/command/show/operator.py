# -*- coding: utf-8 -*-
import optparse
import pymysql
from pit import Pit


def generate_operator():
    settings = Pit.get('altair-dbslave',
                       {'require': {'host': '',
                                    'db': '',
                                    'user': '',
                                    'passwd': '',
                                    }})

    host = settings['host']
    db = settings['db']
    user = settings['user']
    passwd = settings['passwd']

    client = pymysql.connect(host=host, db=db,
                             user=user, passwd=passwd)
    cur = client.cursor()
    cur.execute('SET NAMES sjis')
    cur.execute('SELECT `Operator`.id, `OperatorAuth`.login_id, `Organization`.name FROM Operator'
                '  JOIN Organization ON `Operator`.organization_id=`Organization`.id'
                '  JOIN OperatorAuth ON `OperatorAuth`.operator_id=`Operator`.id'
                '  ORDER BY `Organization`.id'
                )
    entries = cur.fetchall()
    for opeid, login_id, org_name in entries:
        yield str(opeid), login_id, org_name.decode('sjis')


def main(argv):
    parser = optparse.OptionParser()
    opts, args = parser.parse_args(argv)

    for entry in generate_operator():
        print ','.join(entry)
