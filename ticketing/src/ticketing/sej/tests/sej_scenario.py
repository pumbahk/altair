# -*- coding:utf-8 -*-

#
# SEJとの外部結合の為に使ったスクリプト
#

from pyramid.paster import bootstrap
import sqlahelper

session = sqlahelper.get_session()

import datetime
from dateutil.parser import parse
# -*- coding:utf-8 -*-
from ticketing.sej.payment import request_order, request_update_order, request_cancel_order
from ticketing.sej.payment import SejTicketDataXml, SejPaymentType, SejTicketType, SejOrderUpdateReason
from ticketing.sej.models import SejOrder
from ticketing.sej.utils import han2zen

import time

import csv
import optparse
import sys

from os.path import abspath, dirname

BASE_PATH=dirname(__file__)
sys.path.append(abspath(dirname(BASE_PATH)))

from paste.deploy import loadapp

import logging

logging.basicConfig()
log = logging.getLogger(__file__)

def ticket_date_xml(event_name, ticket_price, order_id, number,seat_number):
    ticket_html = u"""<?xml version="1.0" encoding="Shift_JIS" ?>
<TICKET>
<b><![CDATA[:mm U :#000 rg
1e-3 S 134333 2288m134106 2076 133798 1827 133430 1674c133430 3002l133067 3002l133067 567l133436 631l133445 635 133509 644 133509 681c133509 699 133430 748 133430 764c133430 1572l133574 1345l133731 1412 133832 1452 134096 1624c134340 1784 134453 1886 134576 1993c134333 2288l h130856 1803m130804 1618 130733 1461 130638 1305c130911 1200l131025 1382 131087 1572 131121 1698c130856 1803l h131889 1403m131861 1418 131858 1430 131827 1551c131597 2494 130976 2854 130681 3026c130435 2808l131031 2513 131450 2092 131566 1222c131867 1314l131907 1326 131929 1348 131929 1369c131929 1388 131923 1391 131889 1403c130290 1953m130238 1778 130158 1615 130057 1458c130340 1351l130444 1514 130524 1674 130576 1846c130290 1953l h128697 1437m128691 1631 128688 1935 128507 2322c128289 2793 127963 3048 127793 3183c127419 2952l127576 2857 127917 2648 128138 2208c128304 1876 128313 1603 128316 1437c127671 1437l127450 1781 127326 1917 127185 2064c126826 1864l127281 1443 127539 1025 127729 395c128079 521l128098 527 128156 549 128156 582c128156 604 128147 610 128116 619c128086 634 128083 638 128067 678c128018 798 127981 884 127877 1090c129457 1090l129457 1437l128697 1437l h125208 1858m125085 2467 124833 2756 124313 3094c124015 2832l124513 2549 124732 2316 124833 1858c123738 1858l123738 1517l124870 1517l124873 1486 124876 1428 124876 1326c124876 1219 124873 1151 124858 1080c124574 1145 124409 1172 124138 1197c123972 890l124200 877 124848 834 125503 499c125755 733l125764 742 125792 773 125792 795c125792 807 125786 813 125777 816c125678 816l125660 816 125657 819 125632 828c125530 874 125454 911 125242 979c125245 1090 125254 1262 125251 1369c125251 1449 125248 1465 125248 1517c126068 1517l126068 1858l125208 1858l h115365 493m115365 112l114663 494l114663 874l115365 493l h113328 1188m114114 1188l114114 1516l113328 1516l113328 1188l h113328 584m114114 584l114114 872l113328 872l113328 584l h115365 1970m115365 1598l114663 1216l114663 1597l115351 1970l113894 1970l113894 1839l114465 1839l114465 265l113857 265l113937 0l113563 0l113482 265l112980 265l112980 1839l113542 1839l113542 1970l112096 1970l112782 1598l112782 1217l112082 1598l112082 2311l113256 2311l113008 2549 112621 2829 112054 3026c112000 3045l112000 3403l112108 3365l112723 3143 113204 2857 113542 2513c113542 3454l113894 3454l113894 2513l114236 2863 114720 3147 115335 3358c115442 3395l115442 3037l115387 3019l114818 2830 114430 2550 114179 2311c115365 2311l115365 1970l115365 1970l h112082 112m112082 493l112782 873l112782 493l112082 112l h122441 476m122441 128l118999 128l118999 476l120498 476l120498 987l120498 1121 120495 1192 120489 1288c119106 1288l119106 1640l120436 1640l120337 2041 120026 2672 119046 3019c118992 3039l118992 3447l119102 3405l120138 3008 120526 2560 120711 1991c120935 2570 121467 3035 122328 3405c122441 3454l122441 3032l122386 3014l121574 2749 121091 2137 120959 1640c122323 1640l122323 1288l120881 1288l120871 1218 120864 1134 120864 987c120864 476l122441 476l117028 1173m117263 1173l117408 1173 117526 1293 117526 1439c117526 1584 117408 1703 117263 1703c117028 1703l117028 1173l117563 1960m117748 1856 117866 1656 117866 1439c117866 1105 117596 833 117263 833c116688 833l116688 2621l117028 2621l117028 2043l117203 2043l117217 2063 117619 2621 117619 2621c118037 2621l118037 2621 117593 2002 117563 1960c118902 1727m118902 2647 118156 3393 117236 3393c116316 3393 115570 2647 115570 1727c115570 807 116316 61 117236 61c118156 61 118902 807 118902 1727c f
:f15 hc 1 S
12 fs :b hc 15 0 m 93 12 "BLUE MAN GROUP IN TOKYO" X pc 10 fs
15 8 m 93 5 "%(event_name)s %(number)s" X
15 13 m 93 10 "2012年 08月 31日(金)<br /> 12:30 開場 13:00 開演" X
65 13 m 93 10 "ポンチョ席 1列%(seat_number)s番<br/>\\%(ticket_price)s(税込)" X
6 fs
15 25 m 90 10 "主催: ブルーマングループ IN 東京、LLP<br/>お問合せ: ブルーマングループ東京公演事務局 03-5414-3255<br/>後援: 東京都、米国大使館、港区、東京メトロ<br/>営利目的の転売禁止<br/>4歳以下入場不可" X
6 fs
15 42 m 30 2 "予約番号" X 28 42 m 30 2 "%(order_id)s" X
15 44 m 20 2 "払込表番号" X 28 44 m 30 2 :FIXTAG05 xn sxn X
55 44 m 28 2 :FIXTAG04 xn sxn X
15 46 m 6 2 "店名" X 20 46 m 60 2 :FIXTAG02 xn sxn X
55 46 m 6 2 "店番" X 60 46 m 10 2 :FIXTAG03 xn sxn X
95 46 m 30 2 :FIXTAG06 xn sxn X
8 fs
:b hc 112 5 m 30 11 "BLUE MAN GROUP IN TOKYO" X pc
112 16 m 30 12 "開催日 2012年<br/>7月9日(土)<br/>開場 12:30<br/>開演 13:00<br/>" X
112 32 m 30 15 "ポンチョ席<br/>1列%(seat_number)s番<br/>\\%(ticket_price)s(税込)" X
6 fs 112 46 m 30 4 "0509-1234" X
]]></b>
<FIXTAG01></FIXTAG01>
<FIXTAG02></FIXTAG02>
<FIXTAG03></FIXTAG03>
<FIXTAG04></FIXTAG04>
<FIXTAG05></FIXTAG05>
<FIXTAG06></FIXTAG06>
</TICKET>""" % dict(event_name=event_name, ticket_price=ticket_price, order_id=order_id, number=number,seat_number=seat_number)
    return ticket_html

payment_type_index = {
    '代引き発券'        : SejPaymentType.CashOnDelivery,
    '払戻し（代引き）'        : SejPaymentType.CashOnDelivery,
    '代済み発券'        : SejPaymentType.Paid,
    '前払い後日発券'     : SejPaymentType.Prepayment,
    '前払い後日発券（前払い）'     : SejPaymentType.Prepayment,
    '前払い後日発券（発券）'     : SejPaymentType.Prepayment,
    '前払い'          : SejPaymentType.PrepaymentOnly
}

def load_tsv_file():
    csv_file = open(BASE_PATH + '/data/scenario1.tsv')
    order_id = 600
    seat_number = 1
    for row in csv.reader(csv_file, delimiter='\t'):

        ticket_total    = row[13].split('→')[0]
        commission_fee  = row[14].split('→')[0]
        ticketing_fee   = row[15].split('→')[0]
        total = row[16].split('→')[0]
#        if order_id < 669:
#            order_id += 1
#            continue
        order_number            = u'%012d' % order_id
        order_id += 1

        total_ticket_num      = int(row[17]if row[17] else 0)
        e_ticket_num    = int(row[18]if row[18] else 0)
        ticket_num = total_ticket_num - e_ticket_num

        number = "%d-%d-%d-%d-%d-%d" % (int(row[0]),int(row[1]),int(row[2]),int(row[3]),int(row[4]),int(row[5])),
        print "ticket num %d" % total_ticket_num
        tickets = list()
        for i in range(0,ticket_num):
            ticket = dict(
                ticket_type         = SejTicketType.TicketWithBarcode,
                event_name          = u'１',
                performance_name    = u'１',
                ticket_template_id  = u'TTTS000001',
                performance_datetime= datetime.datetime(2012,8,31,18,00),
                xml = SejTicketDataXml(ticket_date_xml(u'テスト:%s' % order_number, '100', order_id, number, seat_number))
            )
            tickets.append(ticket)
            seat_number += 1

        for i in range(0, e_ticket_num):
            ticket = dict(
                ticket_type         = SejTicketType.ExtraTicketWithBarcode,
                event_name          = u'イベント名',
                performance_name    = u'１２３４５６７８９０１２３４５６７８９０',
                ticket_template_id  = u'TTTS000001',
                performance_datetime= datetime.datetime(2012,8,31,18,00),
                xml = SejTicketDataXml(ticket_date_xml(u'テスト:%s' % order_number, '100', order_id, number, ''))
            )
            tickets.append(ticket)

        request_order(
            order_id = order_number,
            total               = int(total),
            ticket_total        = int(ticket_total),
            ticketing_fee       = int(ticketing_fee),
            commission_fee      = int(commission_fee),
            payment_due_at    = parse(row[19]),
            ticketing_due_at  = parse(row[20]),
            ticketing_start_at= parse(row[21].split('→')[0]),
            shop_name           = u'楽天チケット',
            contact_01          = u'00-0000-0000',
            contact_02          = u'ブルーマングループ東京公演事務局 ',
            username            = u'試験ユーザー',
            username_kana       = u'テストユーザー',
            tel                 = u'0000000000',
            zip                 = u'1070062',
            email               = u'dev+sejtest@ticketstar.jp',
            payment_type        = payment_type_index[row[8]],
            regrant_number_due_at = datetime.datetime(2012,7,9,23,59,59),
            tickets = tickets,
        )


def main(argv=sys.argv):
    session.configure(autocommit=True, extension=[])

    parser = optparse.OptionParser(
        description=__doc__,
        usage='%prog [options]',
    )
    parser.add_option('-C', '--config',
        dest='config',
        help='Path to configuration file (defaults to $CWD/development.ini)',
        metavar='FILE'
    )

    options, args = parser.parse_args(argv[1:])

    # configuration
    config = options.config
    if config is None:
        print 'You must give a config file'
        return
    app = loadapp('config:%s' % config, 'main')
    settings = app.registry.settings

    log.debug('test')

    load_tsv_file()

if __name__ == u"__main__":
    main(sys.argv)

