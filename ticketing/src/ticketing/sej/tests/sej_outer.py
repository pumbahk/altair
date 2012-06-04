# -*- coding:utf-8 -*-



from pyramid.paster import bootstrap
import sqlahelper

session = sqlahelper.get_session()

import datetime
# -*- coding:utf-8 -*-
from ticketing.sej.payment import request_order, request_update_order, request_cancel_order
from ticketing.sej.payment import SejTicketDataXml, SejPaymentType, SejTicketType, SejOrderUpdateReason
from ticketing.sej.models import SejOrder

import time

def payment_test():
    ''' 注文受付：【代引き】
    '''
    # 決済要求
    print ''' 1-①：XXXXXXXXXXXXX(注文更新、注文取消し用)'''
    sejTicketOrder = request_order(
        shop_name       = u'楽天チケット',
        contact_01      = u'contact',
        contact_02      = u'連絡先2',
        order_id        = u"%012d" % int(datetime.datetime.now().strftime('%y%m%d%H%M%S')),
        username        = u"小泉守義",
        username_kana   = u'コイズミモリヨシ',
        tel             = u'0312341234',
        zip             = u'1070062',
        email           = u'dev@ticketstar.jp',
        # 20000	0	420	20420
        total           = 420,
        ticket_total    = 20000,
        commission_fee  = 0,
        ticketing_fee   = 420,
        payment_type    = SejPaymentType.Paid,
        payment_due_datetime = datetime.datetime(2012,7,30,7,00), #u'201207300700',
        regrant_number_datetime = datetime.datetime(2012,7,30,7,00), # u'201207300700',
        tickets = [
            dict(
                ticket_type         = SejTicketType.TicketWithBarcode,
                event_name          = u'注文更新、注文取消し用興行',
                performance_name    = u'注文更新、注文取消し用公演',
                ticket_template_id  = u'TTTS000001',
                performance_datetime= datetime.datetime(2012,8,31,18,00),
                xml = SejTicketDataXml(u'''<?xml version="1.0" encoding="UTF-8" ?>
                <TICKET>
                  <TEST1>test&#x20;test</TEST1>
                  <TEST2><![CDATA[TEST [] >M>J TEST@&nbsp;]]></TEST2>
                  <TEST3>&#x3000;</TEST3>
                  <FIXTAG01></FIXTAG01>
                  <FIXTAG02></FIXTAG02>
                  <FIXTAG03></FIXTAG03>
                  <FIXTAG04></FIXTAG04>
                  <FIXTAG05></FIXTAG05>
                  <FIXTAG06></FIXTAG06>
                </TICKET>''')
            )
        ]
    )

def payment_test_cod_r_c_c():
    ''' 注文受付：【代引き】
    '''
    # 決済要求
    print ''' 1-①：XXXXXXXXXXXXX(注文更新、注文取消し用)'''
    sejTicketOrder = request_order(
        shop_name       = u'楽天チケット',
        contact_01      = u'contact',
        contact_02      = u'連絡先2',
        order_id        = u"%012d" % int(datetime.datetime.now().strftime('%y%m%d%H%M%S')),
        username        = u"小泉守義",
        username_kana   = u'コイズミモリヨシ',
        tel             = u'0312341234',
        zip             = u'1070062',
        email           = u'dev@ticketstar.jp',
        total           = 15000,
        ticket_total    = 13000,
        commission_fee  = 1000,
        ticketing_fee   = 1000,
        payment_type    = SejPaymentType.CashOnDelivery,
        payment_due_datetime = datetime.datetime(2012,7,30,7,00), #u'201207300700',
        regrant_number_datetime = datetime.datetime(2012,7,30,7,00), # u'201207300700',
        tickets = [
            dict(
                ticket_type         = SejTicketType.TicketWithBarcode,
                event_name          = u'注文更新、注文取消し用興行',
                performance_name    = u'注文更新、注文取消し用公演',
                ticket_template_id  = u'TTTS000001',
                performance_datetime= datetime.datetime(2012,8,31,18,00),
                xml = SejTicketDataXml(u'''<?xml version="1.0" encoding="UTF-8" ?>
                <TICKET>
                  <TEST1>test&#x20;test</TEST1>
                  <TEST2><![CDATA[TEST [] >M>J TEST@&nbsp;]]></TEST2>
                  <TEST3>&#x3000;</TEST3>
                  <FIXTAG01></FIXTAG01>
                  <FIXTAG02></FIXTAG02>
                  <FIXTAG03></FIXTAG03>
                  <FIXTAG04></FIXTAG04>
                  <FIXTAG05></FIXTAG05>
                  <FIXTAG06></FIXTAG06>
                </TICKET>''')
            )
        ]
    )
    time.sleep(2)
    print ''' 1-②：XXXXXXXXXXXXX(入金、払戻用)'''
    request_order(
        shop_name       = u'楽天チケット',
        contact_01      = u'contact',
        contact_02      = u'連絡先2',
        order_id        = u"%012d" % int(datetime.datetime.now().strftime('%y%m%d%H%M%S')),
        username        = u"お客様氏名",
        username_kana   = u'コイズミモリヨシ',
        tel             = u'0312341234',
        zip             = u'1070062',
        email           = u'dev@ticketstar.jp',
        total           = 15000,
        ticket_total    = 13000,
        commission_fee  = 1000,
        ticketing_fee   = 1000,
        payment_type    = SejPaymentType.CashOnDelivery,
        payment_due_datetime = datetime.datetime(2012,7,30,7,00), #u'201207300700',
        regrant_number_datetime = datetime.datetime(2012,7,30,7,00), # u'201207300700',
        tickets = [
            dict(
                ticket_type         = SejTicketType.TicketWithBarcode,
                event_name          = u'入金、払戻用興行',
                performance_name    = u'入金、払戻用公演',
                ticket_template_id  = u'TTTS000001',
                performance_datetime= datetime.datetime(2012,8,31,18,00),
                xml = SejTicketDataXml(u'''<?xml version="1.0" encoding="UTF-8" ?>
                <TICKET>
                  <TEST1>test&#x20;test</TEST1>
                  <TEST2><![CDATA[TEST [] >M>J TEST@&nbsp;]]></TEST2>
                  <TEST3>&#x3000;</TEST3>
                  <FIXTAG01></FIXTAG01>
                  <FIXTAG02></FIXTAG02>
                  <FIXTAG03></FIXTAG03>
                  <FIXTAG04></FIXTAG04>
                  <FIXTAG05></FIXTAG05>
                  <FIXTAG06></FIXTAG06>
                </TICKET>''')
            )
        ]
    )

    time.sleep(2)
    print ''' 1-③：XXXXXXXXXXXXX(再付番、SVC取消用)'''
    request_order(
        shop_name       = u'楽天チケット',
        contact_01      = u'contact',
        contact_02      = u'連絡先2',
        order_id        = u"%012d" % int(datetime.datetime.now().strftime('%y%m%d%H%M%S')),
        username        = u"お客様氏名",
        username_kana   = u'コイズミモリヨシ',
        tel             = u'0312341234',
        zip             = u'1070062',
        email           = u'dev@ticketstar.jp',
        total           = 15000,
        ticket_total    = 13000,
        commission_fee  = 1000,
        ticketing_fee   = 1000,
        payment_type    = SejPaymentType.CashOnDelivery,
        payment_due_datetime = datetime.datetime(2012,7,30,7,00), #u'201207300700',
        regrant_number_datetime = datetime.datetime(2012,7,30,7,00), # u'201207300700',
        tickets = [
            dict(
                ticket_type         = SejTicketType.TicketWithBarcode,
                event_name          = u'再付番ＳＶＣ取消用興行',
                performance_name    = u'再付番ＳＶＣ取消用公演',
                ticket_template_id  = u'TTTS000001',
                performance_datetime= datetime.datetime(2012,8,31,18,00),
                xml = SejTicketDataXml(u'''<?xml version="1.0" encoding="UTF-8" ?>
                <TICKET>
                  <TEST1>test&#x20;test</TEST1>
                  <TEST2><![CDATA[TEST [] >M>J TEST@&nbsp;]]></TEST2>
                  <TEST3>&#x3000;</TEST3>
                  <FIXTAG01></FIXTAG01>
                  <FIXTAG02></FIXTAG02>
                  <FIXTAG03></FIXTAG03>
                  <FIXTAG04></FIXTAG04>
                  <FIXTAG05></FIXTAG05>
                  <FIXTAG06></FIXTAG06>
                </TICKET>''')
            )
        ]
    )

    time.sleep(2)
    print ''' 1-④：XXXXXXXXXXXXX(発券期限切れ用)'''
    request_order(
        shop_name       = u'楽天チケット',
        contact_01      = u'contact',
        contact_02      = u'連絡先2',
        order_id        = u"%012d" % int(datetime.datetime.now().strftime('%y%m%d%H%M%S')),
        username        = u"お客様氏名",
        username_kana   = u'コイズミモリヨシ',
        tel             = u'0312341234',
        zip             = u'1070062',
        email           = u'dev@ticketstar.jp',
        total           = 15000,
        ticket_total    = 13000,
        commission_fee  = 1000,
        ticketing_fee   = 1000,
        payment_type    = SejPaymentType.CashOnDelivery,
        payment_due_datetime = datetime.datetime(2012,7,30,7,00), #u'201207300700',
        regrant_number_datetime = datetime.datetime(2012,7,30,7,00), # u'201207300700',
        tickets = [
            dict(
                ticket_type         = SejTicketType.TicketWithBarcode,
                event_name          = u'発券期限切興行',
                performance_name    = u'発券期限切公演',
                ticket_template_id  = u'TTTS000001',
                performance_datetime= datetime.datetime(2012,8,31,18,00),
                xml = SejTicketDataXml(u'''<?xml version="1.0" encoding="UTF-8" ?>
                <TICKET>
                  <TEST1>test&#x20;test</TEST1>
                  <TEST2><![CDATA[TEST [] >M>J TEST@&nbsp;]]></TEST2>
                  <TEST3>&#x3000;</TEST3>
                  <FIXTAG01></FIXTAG01>
                  <FIXTAG02></FIXTAG02>
                  <FIXTAG03></FIXTAG03>
                  <FIXTAG04></FIXTAG04>
                  <FIXTAG05></FIXTAG05>
                  <FIXTAG06></FIXTAG06>
                </TICKET>''')
            )
        ]
    )

    time.sleep(10)
    #注文変更要求
    sejTicketOrder = request_update_order(
        update_reason   = SejOrderUpdateReason.Change,
        total           = 15003,
        ticket_total    = 13001,
        commission_fee  = 1001,
        ticketing_fee   = 1001,
        payment_type    = SejPaymentType.CashOnDelivery,
        payment_due_datetime =  datetime.datetime(2012,7,30,8,00) ,
        ticketing_start_datetime = None,
        ticketing_due_datetime = None,
        regrant_number_datetime = datetime.datetime(2012,7,30,7,00), # u'201207300700',
        tickets = [
                    dict(
                        ticket_type         = SejTicketType.TicketWithBarcode,
                        event_name          = u'注文更新、注文取消し用興行ｕ',
                        performance_name    = u'注文更新、注文取消し用公演ｕ',
                        ticket_template_id  = u'TTTS000001',
                        performance_datetime= datetime.datetime(2012,8,31,18,00),
                        xml = SejTicketDataXml(u'''<?xml version="1.0" encoding="UTF-8" ?>
                        <TICKET>
                          <TEST1>test&#x20;test</TEST1>
                          <TEST2><![CDATA[TEST [] >M>J TEST@&nbsp;]]></TEST2>
                          <TEST3>&#x3000;</TEST3>
                          <FIXTAG01></FIXTAG01>
                          <FIXTAG02></FIXTAG02>
                          <FIXTAG03></FIXTAG03>
                          <FIXTAG04></FIXTAG04>
                          <FIXTAG05></FIXTAG05>
                          <FIXTAG06></FIXTAG06>
                        </TICKET>''')
                    )
                ],
        condition = dict(
            order_id = sejTicketOrder.order_id,
            billing_number = sejTicketOrder.billing_number,
            exchange_number = sejTicketOrder.exchange_number
        )

    )


    time.sleep(10)
    # 注文取消要求
    request_cancel_order(
        order_id            = sejTicketOrder.order_id,
        billing_number      = sejTicketOrder.billing_number,
        exchange_number     = sejTicketOrder.exchange_number
    )


def payment_test_pre_r_c_c():
    ''' 注文受付：【前払後日発券】
    '''
    # 決済要求
    print ''' 2-①：XXXXXXXXXXXXX(注文更新、注文取消し用)'''
    sejTicketOrder = request_order(
        shop_name       = u'楽天チケット',
        contact_01      = u'contact',
        contact_02      = u'連絡先2',
        order_id        = u"%012d" % int(datetime.datetime.now().strftime('%y%m%d%H%M%S')),
        username        = u"小泉守義",
        username_kana   = u'コイズミモリヨシ',
        tel             = u'0312341234',
        zip             = u'1070062',
        email           = u'dev@ticketstar.jp',
        total           = 15000,
        ticket_total    = 13000,
        commission_fee  = 1000,
        ticketing_fee   = 1000,
        payment_type    = SejPaymentType.Prepayment,
        payment_due_datetime = datetime.datetime(2012,7,30,7,00), #u'201207300700',
        regrant_number_datetime = datetime.datetime(2012,7,30,7,00), # u'201207300700',
        tickets = [
            dict(
                ticket_type         = SejTicketType.TicketWithBarcode,
                event_name          = u'注文更新、注文取消し用興行',
                performance_name    = u'注文更新、注文取消し用公演',
                ticket_template_id  = u'TTTS000001',
                performance_datetime= datetime.datetime(2012,8,31,18,00),
                xml = SejTicketDataXml(u'''<?xml version="1.0" encoding="UTF-8" ?>
                <TICKET>
                  <TEST1>test&#x20;test</TEST1>
                  <TEST2><![CDATA[TEST [] >M>J TEST@&nbsp;]]></TEST2>
                  <TEST3>&#x3000;</TEST3>
                  <FIXTAG01></FIXTAG01>
                  <FIXTAG02></FIXTAG02>
                  <FIXTAG03></FIXTAG03>
                  <FIXTAG04></FIXTAG04>
                  <FIXTAG05></FIXTAG05>
                  <FIXTAG06></FIXTAG06>
                </TICKET>''')
            )
        ]
    )
    time.sleep(10)
    print ''' 2-②：XXXXXXXXXXXXX(入金、払戻用)'''
    request_order(
        shop_name       = u'楽天チケット',
        contact_01      = u'contact',
        contact_02      = u'連絡先2',
        order_id        = u"%012d" % int(datetime.datetime.now().strftime('%y%m%d%H%M%S')),
        username        = u"お客様氏名",
        username_kana   = u'コイズミモリヨシ',
        tel             = u'0312341234',
        zip             = u'1070062',
        email           = u'dev@ticketstar.jp',
        total           = 15000,
        ticket_total    = 13000,
        commission_fee  = 1000,
        ticketing_fee   = 1000,
        payment_type    = SejPaymentType.Prepayment,
        payment_due_datetime = datetime.datetime(2012,7,30,7,00), #u'201207300700',
        regrant_number_datetime = datetime.datetime(2012,7,30,7,00), # u'201207300700',
        tickets = [
            dict(
                ticket_type         = SejTicketType.TicketWithBarcode,
                event_name          = u'入金、払戻用興行',
                performance_name    = u'入金、払戻用公演',
                ticket_template_id  = u'TTTS000001',
                performance_datetime= datetime.datetime(2012,8,31,18,00),
                xml = SejTicketDataXml(u'''<?xml version="1.0" encoding="UTF-8" ?>
                <TICKET>
                  <TEST1>test&#x20;test</TEST1>
                  <TEST2><![CDATA[TEST [] >M>J TEST@&nbsp;]]></TEST2>
                  <TEST3>&#x3000;</TEST3>
                  <FIXTAG01></FIXTAG01>
                  <FIXTAG02></FIXTAG02>
                  <FIXTAG03></FIXTAG03>
                  <FIXTAG04></FIXTAG04>
                  <FIXTAG05></FIXTAG05>
                  <FIXTAG06></FIXTAG06>
                </TICKET>''')
            )
        ]
    )


    time.sleep(10)
    #注文変更要求
    sejTicketOrder = request_update_order(
        update_reason   = SejOrderUpdateReason.Change,
        total           = 15003,
        ticket_total    = 13001,
        commission_fee  = 1001,
        ticketing_fee   = 1001,
        payment_type    = SejPaymentType.Prepayment,
        payment_due_datetime =  datetime.datetime(2012,7,30,8,00) ,
        ticketing_start_datetime = None,
        ticketing_due_datetime = None,
        regrant_number_datetime = datetime.datetime(2012,7,30,7,00), # u'201207300700',
        tickets = [
                    dict(
                        ticket_type         = SejTicketType.TicketWithBarcode,
                        event_name          = u'注文更新、注文取消し用興行ｕ',
                        performance_name    = u'注文更新、注文取消し用公演ｕ',
                        ticket_template_id  = u'TTTS000001',
                        performance_datetime= datetime.datetime(2012,8,31,18,00),
                        xml = SejTicketDataXml(u'''<?xml version="1.0" encoding="UTF-8" ?>
                        <TICKET>
                          <TEST1>test&#x20;test</TEST1>
                          <TEST2><![CDATA[TEST [] >M>J TEST@&nbsp;]]></TEST2>
                          <TEST3>&#x3000;</TEST3>
                          <FIXTAG01></FIXTAG01>
                          <FIXTAG02></FIXTAG02>
                          <FIXTAG03></FIXTAG03>
                          <FIXTAG04></FIXTAG04>
                          <FIXTAG05></FIXTAG05>
                          <FIXTAG06></FIXTAG06>
                        </TICKET>''')
                    )
                ],
        condition = dict(
            order_id = sejTicketOrder.order_id,
            billing_number = sejTicketOrder.billing_number,
            exchange_number = sejTicketOrder.exchange_number
        )

    )


    time.sleep(10)
    # 注文取消要求
    request_cancel_order(
        order_id            = sejTicketOrder.order_id,
        billing_number      = sejTicketOrder.billing_number,
        exchange_number     = sejTicketOrder.exchange_number
    )

def payment_test_paid_r_c_c():
    ''' 注文受付：【代済発券】
    '''
    # 決済要求
    print ''' 3-①：XXXXXXXXXXXXX(注文更新、注文取消し用)'''
    sejTicketOrder = request_order(
        shop_name       = u'楽天チケット',
        contact_01      = u'contact',
        contact_02      = u'連絡先2',
        order_id        = u"%012d" % int(datetime.datetime.now().strftime('%y%m%d%H%M%S')),
        username        = u"小泉守義",
        username_kana   = u'コイズミモリヨシ',
        tel             = u'0312341234',
        zip             = u'1070062',
        email           = u'dev@ticketstar.jp',
        total           = 15000,
        ticket_total    = 13000,
        commission_fee  = 1000,
        ticketing_fee   = 1000,
        payment_type    = SejPaymentType.Paid,
        payment_due_datetime = datetime.datetime(2012,7,30,7,00), #u'201207300700',
        regrant_number_datetime = datetime.datetime(2012,7,30,7,00), # u'201207300700',
        tickets = [
            dict(
                ticket_type         = SejTicketType.TicketWithBarcode,
                event_name          = u'注文更新、注文取消し用興行',
                performance_name    = u'注文更新、注文取消し用公演',
                ticket_template_id  = u'TTTS000001',
                performance_datetime= datetime.datetime(2012,8,31,18,00),
                xml = SejTicketDataXml(u'''<?xml version="1.0" encoding="UTF-8" ?>
                <TICKET>
                  <TEST1>test&#x20;test</TEST1>
                  <TEST2><![CDATA[TEST [] >M>J TEST@&nbsp;]]></TEST2>
                  <TEST3>&#x3000;</TEST3>
                  <FIXTAG01></FIXTAG01>
                  <FIXTAG02></FIXTAG02>
                  <FIXTAG03></FIXTAG03>
                  <FIXTAG04></FIXTAG04>
                  <FIXTAG05></FIXTAG05>
                  <FIXTAG06></FIXTAG06>
                </TICKET>''')
            )
        ]
    )
    time.sleep(10)
    print ''' 3-②：XXXXXXXXXXXXX(発券、払戻、払戻取消用)'''
    request_order(
        shop_name       = u'楽天チケット',
        contact_01      = u'contact',
        contact_02      = u'連絡先2',
        order_id        = u"%012d" % int(datetime.datetime.now().strftime('%y%m%d%H%M%S')),
        username        = u"お客様氏名",
        username_kana   = u'コイズミモリヨシ',
        tel             = u'0312341234',
        zip             = u'1070062',
        email           = u'dev@ticketstar.jp',
        total           = 15000,
        ticket_total    = 13000,
        commission_fee  = 1000,
        ticketing_fee   = 1000,
        payment_type    = SejPaymentType.Paid,
        payment_due_datetime = datetime.datetime(2012,7,30,7,00), #u'201207300700',
        regrant_number_datetime = datetime.datetime(2012,7,30,7,00), # u'201207300700',
        tickets = [
            dict(
                ticket_type         = SejTicketType.TicketWithBarcode,
                event_name          = u'入金、払戻用興行',
                performance_name    = u'入金、払戻用公演',
                ticket_template_id  = u'TTTS000001',
                performance_datetime= datetime.datetime(2012,8,31,18,00),
                xml = SejTicketDataXml(u'''<?xml version="1.0" encoding="UTF-8" ?>
                <TICKET>
                  <TEST1>test&#x20;test</TEST1>
                  <TEST2><![CDATA[TEST [] >M>J TEST@&nbsp;]]></TEST2>
                  <TEST3>&#x3000;</TEST3>
                  <FIXTAG01></FIXTAG01>
                  <FIXTAG02></FIXTAG02>
                  <FIXTAG03></FIXTAG03>
                  <FIXTAG04></FIXTAG04>
                  <FIXTAG05></FIXTAG05>
                  <FIXTAG06></FIXTAG06>
                </TICKET>''')
            )
        ]
    )
    print ''' 3-③：XXXXXXXXXXXXX(発券、発券取消用) '''
    request_order(
        shop_name       = u'楽天チケット',
        contact_01      = u'contact',
        contact_02      = u'連絡先2',
        order_id        = u"%012d" % int(datetime.datetime.now().strftime('%y%m%d%H%M%S')),
        username        = u"お客様氏名",
        username_kana   = u'コイズミモリヨシ',
        tel             = u'0312341234',
        zip             = u'1070062',
        email           = u'dev@ticketstar.jp',
        total           = 15000,
        ticket_total    = 13000,
        commission_fee  = 1000,
        ticketing_fee   = 1000,
        payment_type    = SejPaymentType.Paid,
        payment_due_datetime = datetime.datetime(2012,7,30,7,00), #u'201207300700',
        regrant_number_datetime = datetime.datetime(2012,7,30,7,00), # u'201207300700',
        tickets = [
            dict(
                ticket_type         = SejTicketType.TicketWithBarcode,
                event_name          = u'発券、発券取消用興行',
                performance_name    = u'発券、発券取消用公演',
                ticket_template_id  = u'TTTS000001',
                performance_datetime= datetime.datetime(2012,8,31,18,00),
                xml = SejTicketDataXml(u'''<?xml version="1.0" encoding="UTF-8" ?>
                <TICKET>
                  <TEST1>test&#x20;test</TEST1>
                  <TEST2><![CDATA[TEST [] >M>J TEST@&nbsp;]]></TEST2>
                  <TEST3>&#x3000;</TEST3>
                  <FIXTAG01></FIXTAG01>
                  <FIXTAG02></FIXTAG02>
                  <FIXTAG03></FIXTAG03>
                  <FIXTAG04></FIXTAG04>
                  <FIXTAG05></FIXTAG05>
                  <FIXTAG06></FIXTAG06>
                </TICKET>''')
            )
        ]
    )
    time.sleep(10)
    #注文変更要求
    sejTicketOrder = request_update_order(
        update_reason   = SejOrderUpdateReason.Change,
        total           = 15003,
        ticket_total    = 13001,
        commission_fee  = 1001,
        ticketing_fee   = 1001,
        payment_type    = SejPaymentType.Paid,
        payment_due_datetime =  datetime.datetime(2012,7,30,8,00) ,
        ticketing_start_datetime = None,
        ticketing_due_datetime = None,
        regrant_number_datetime = datetime.datetime(2012,7,30,7,00), # u'201207300700',
        tickets = [
                    dict(
                        ticket_type         = SejTicketType.TicketWithBarcode,
                        event_name          = u'注文更新、注文取消し用興行ｕ',
                        performance_name    = u'注文更新、注文取消し用公演ｕ',
                        ticket_template_id  = u'TTTS000001',
                        performance_datetime= datetime.datetime(2012,8,31,18,00),
                        xml = SejTicketDataXml(u'''<?xml version="1.0" encoding="UTF-8" ?>
                        <TICKET>
                          <TEST1>test&#x20;test</TEST1>
                          <TEST2><![CDATA[TEST [] >M>J TEST@&nbsp;]]></TEST2>
                          <TEST3>&#x3000;</TEST3>
                          <FIXTAG01></FIXTAG01>
                          <FIXTAG02></FIXTAG02>
                          <FIXTAG03></FIXTAG03>
                          <FIXTAG04></FIXTAG04>
                          <FIXTAG05></FIXTAG05>
                          <FIXTAG06></FIXTAG06>
                        </TICKET>''')
                    )
                ],
        condition = dict(
            order_id = sejTicketOrder.order_id,
            billing_number = sejTicketOrder.billing_number,
            exchange_number = sejTicketOrder.exchange_number
        )

    )


    time.sleep(10)
    # 注文取消要求
    request_cancel_order(
        order_id            = sejTicketOrder.order_id,
        billing_number      = sejTicketOrder.billing_number,
        exchange_number     = sejTicketOrder.exchange_number
    )


def payment_test_p_only_r_c_c():
    ''' 注文受付：【代引き】
    '''
    # 決済要求
    print ''' 1-①：XXXXXXXXXXXXX(注文更新、注文取消し用)'''
    sejTicketOrder = request_order(
        shop_name       = u'楽天チケット',
        contact_01      = u'contact',
        contact_02      = u'連絡先2',
        order_id        = u"%012d" % int(datetime.datetime.now().strftime('%y%m%d%H%M%S')),
        username        = u"小泉守義",
        username_kana   = u'コイズミモリヨシ',
        tel             = u'0312341234',
        zip             = u'1070062',
        email           = u'dev@ticketstar.jp',
        total           = 14000,
        ticket_total    = 13000,
        commission_fee  = 1000,
        ticketing_fee   = None,
        payment_type    = SejPaymentType.PrepaymentOnly,
        payment_due_datetime = datetime.datetime(2012,7,30,7,00), #u'201207300700',
        regrant_number_datetime = datetime.datetime(2012,7,30,7,00), # u'201207300700',
    )

    time.sleep(2)
    print ''' 4-②：XXXXXXXXXXXXX(入金用)'''
    request_order(
        shop_name       = u'楽天チケット',
        contact_01      = u'contact',
        contact_02      = u'連絡先2',
        order_id        = u"%012d" % int(datetime.datetime.now().strftime('%y%m%d%H%M%S')),
        username        = u"お客様氏名",
        username_kana   = u'コイズミモリヨシ',
        tel             = u'0312341234',
        zip             = u'1070062',
        email           = u'dev@ticketstar.jp',
        total           = 14000,
        ticket_total    = 13000,
        commission_fee  = 1000,
        ticketing_fee   = None,
        payment_type    = SejPaymentType.PrepaymentOnly,
        payment_due_datetime = datetime.datetime(2012,7,30,7,00), #u'201207300700',
        regrant_number_datetime = datetime.datetime(2012,7,30,7,00), # u'201207300700',
    )

    time.sleep(2)
    print ''' 4-③：XXXXXXXXXXXXX(入金期限切れデータ用)'''
    request_order(
        shop_name       = u'楽天チケット',
        contact_01      = u'contact',
        contact_02      = u'連絡先2',
        order_id        = u"%012d" % int(datetime.datetime.now().strftime('%y%m%d%H%M%S')),
        username        = u"お客様氏名",
        username_kana   = u'コイズミモリヨシ',
        tel             = u'0312341234',
        zip             = u'1070062',
        email           = u'dev@ticketstar.jp',
        total           = 14000,
        ticket_total    = 13000,
        commission_fee  = 1000,
        ticketing_fee   = None,
        payment_type    = SejPaymentType.PrepaymentOnly,
        payment_due_datetime = datetime.datetime(2012,7,30,7,00), #u'201207300700',
        regrant_number_datetime = datetime.datetime(2012,7,30,7,00), # u'201207300700',
    )
    time.sleep(2)
    print ''' 4-④：XXXXXXXXXXXXX(入金、入金取消用)'''
    request_order(
        shop_name       = u'楽天チケット',
        contact_01      = u'contact',
        contact_02      = u'連絡先2',
        order_id        = u"%012d" % int(datetime.datetime.now().strftime('%y%m%d%H%M%S')),
        username        = u"お客様氏名",
        username_kana   = u'コイズミモリヨシ',
        tel             = u'0312341234',
        zip             = u'1070062',
        email           = u'dev@ticketstar.jp',
        total           = 14000,
        ticket_total    = 13000,
        commission_fee  = 1000,
        ticketing_fee   = None,
        payment_type    = SejPaymentType.PrepaymentOnly,
        payment_due_datetime = datetime.datetime(2012,7,30,7,00), #u'201207300700',
        regrant_number_datetime = datetime.datetime(2012,7,30,7,00), # u'201207300700',
    )
    time.sleep(10)
    #注文変更要求
    sejTicketOrder = request_update_order(
        update_reason   = SejOrderUpdateReason.Change,
        total           = 14002,
        ticket_total    = 13001,
        commission_fee  = 1001,
        ticketing_fee   = None,
        payment_type    = SejPaymentType.PrepaymentOnly,
        payment_due_datetime =  datetime.datetime(2012,7,30,8,00) ,
        ticketing_start_datetime = None,
        ticketing_due_datetime = None,
        regrant_number_datetime = datetime.datetime(2012,7,30,7,00), # u'201207300700',
        tickets = [
                    dict(
                        ticket_type         = SejTicketType.TicketWithBarcode,
                        event_name          = u'注文更新、注文取消し用興行ｕ',
                        performance_name    = u'注文更新、注文取消し用公演ｕ',
                        ticket_template_id  = u'TTTS000001',
                        performance_datetime= datetime.datetime(2012,8,31,18,00),
                        xml = SejTicketDataXml(u'''<?xml version="1.0" encoding="UTF-8" ?>
                        <TICKET>
                          <TEST1>test&#x20;test</TEST1>
                          <TEST2><![CDATA[TEST [] >M>J TEST@&nbsp;]]></TEST2>
                          <TEST3>&#x3000;</TEST3>
                          <FIXTAG01></FIXTAG01>
                          <FIXTAG02></FIXTAG02>
                          <FIXTAG03></FIXTAG03>
                          <FIXTAG04></FIXTAG04>
                          <FIXTAG05></FIXTAG05>
                          <FIXTAG06></FIXTAG06>
                        </TICKET>''')
                    )
                ],
        condition = dict(
            order_id = sejTicketOrder.order_id,
            billing_number = sejTicketOrder.billing_number,
            exchange_number = sejTicketOrder.exchange_number
        )

    )


    time.sleep(10)
    # 注文取消要求
    request_cancel_order(
        order_id            = sejTicketOrder.order_id,
        billing_number      = sejTicketOrder.billing_number,
        exchange_number     = sejTicketOrder.exchange_number
    )
import csv
import optparse
import sys

from os.path import abspath, dirname
sys.path.append(abspath(dirname(dirname(__file__))))

from paste.deploy import loadapp

import logging

logging.basicConfig()
log = logging.getLogger(__file__)


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
#    payment_test_cod_r_c_c()
#    payment_test_pre_r_c_c()
#    payment_test_paid_r_c_c()
#    payment_test_p_only_r_c_c()
    payment_test()
#    payment_test_pre_2()
#    payment_test_pay()
if __name__ == u"__main__":
    main(sys.argv)

