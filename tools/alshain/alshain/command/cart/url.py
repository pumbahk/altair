# -*- coding: utf-8 -*-
import optparse
import pymysql
from pit import Pit


def generate_avairable_cart_url(production=False):
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

    client = pymysql.connect(host=host, db=db, user=user, passwd=passwd)

    cur = client.cursor()
    cur.execute('SELECT `Event`.id, `Host`.host_name  FROM `Event`'
                '  JOIN `Performance` ON `Performance`.event_id=`Event`.id'
                '  JOIN `SalesSegment` ON `SalesSegment`.performance_id=`Performance`.id'
                '  JOIN `SalesSegmentGroup` ON `SalesSegment`.sales_segment_group_id=`SalesSegmentGroup`.id'
                '  JOIN `Organization` ON `Event`.organization_id=`Organization`.id'
                '  JOIN `Host` ON `Host`.organization_id=`Organization`.id'
                '  where `Performance`.public=1 AND `Performance`.public=1 AND `SalesSegment`.public=1'
                '  AND `SalesSegmentGroup`.public=1'
                '  AND ( `SalesSegment`.use_default_start_at AND `SalesSegmentGroup`.start_at < NOW()'
                '      OR `SalesSegment`.start_at < NOW() )'
                '  AND ( `SalesSegment`.use_default_end_at AND NOW() < `SalesSegmentGroup`.end_at'
                '      OR NOW() < `SalesSegment`.end_at )'
                )

    event_host = cur.fetchall()
    event_host = filter(lambda event_host: not 'elbtest' in event_host[1], event_host)
    event_host = set(event_host)

    _is_staging = lambda _hostname: 'stg2' in _hostname

    if production:
        event_host = filter(lambda event_host: not _is_staging(event_host[1]), event_host)
    else:  # staging
        event_host = filter(lambda event_host: _is_staging(event_host[1]), event_host)

    for event, host in sorted(event_host):
        url = 'http://{host}/cart/events/{event}'.format(host=host, event=event)
        yield url


def main(argv):
    parser = optparse.OptionParser()
    parser.add_option('--production', default=False, action='store_true')
    opts, args = parser.parse_args()

    for url in generate_avairable_cart_url(opts.production):
        print url
