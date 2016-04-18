# -*- coding: utf-8 -*-
import logging
import sys
import argparse
from datetime import datetime, timedelta
from sqlalchemy.sql import func
from altair.app.ticketing.orders.models import Order, OrderedProduct, OrderedProductItem, OrderedProductItemToken
from altair.app.ticketing.core.models import Stock, StockType, ProductItem, Event
from pyramid.renderers import render_to_response
from pyramid.paster import bootstrap, setup_logging
import sqlahelper

logger = logging.getLogger(__name__)


def main(argv=sys.argv):
    from altair.app.ticketing.core.models import PrintedReportSetting
    from altair.app.ticketing.events.sales_reports.reports import sendmail

    parser = argparse.ArgumentParser()
    parser.add_argument('config')
    args = parser.parse_args()

    setup_logging(args.config)
    env = bootstrap(args.config)
    registry = env['registry']

    logger.info('start send_printed_report batch')

    now = datetime.now().replace(second=0)
    settings = registry.settings

    query = PrintedReportSetting.query \
        .filter(PrintedReportSetting.start_on <= now) \
        .filter(PrintedReportSetting.end_on > now)

    for cnt, report_setting in enumerate(query.all()):
        logger.info('printed_report_setting_id: {0}'.format(report_setting.id))
        if not report_setting.recipients:
            continue

        today = datetime.now()
        yesterday = today - timedelta(days=1)

        date_format = '%Y-%m-%d 00:00'
        period = u"{0} - {1}".format(yesterday.strftime(date_format), today.strftime(date_format))

        event = report_setting.event
        performance_printed_num = {}

        session = sqlahelper.get_session()
        performance_printed_query = session.query(OrderedProductItem, func.count(OrderedProductItemToken.printed_at)) \
            .join(OrderedProductItemToken, OrderedProductItemToken.ordered_product_item_id == OrderedProductItem.id) \
            .join(OrderedProduct, OrderedProductItem.ordered_product_id == OrderedProduct.id)\
            .join(Order, OrderedProduct.order_id == Order.id) \
            .filter(Order.organization_id == event.organization_id) \
            .filter(OrderedProductItemToken.printed_at >= yesterday.strftime(date_format)) \
            .filter(OrderedProductItemToken.printed_at <= today.strftime(date_format)) \
            .group_by(OrderedProductItem.product_item_id)

        for perf in event.performances:
            performance_printed_num[perf.id] = performance_printed_query.filter(Order.performance_id == perf.id).all()

        subject = u"[発券進捗]{0} {1}".format(event.title, today.strftime('%Y-%m-%d'))
        render_param = dict(event=event, period=period, performance_printed_num=performance_printed_num)

        html = render_to_response('altair.app.ticketing:templates/printed_reports/daily.html', render_param)
        sendmail(settings, report_setting.format_emails(), subject, html)
        logger.info('end send_printed_report batch (sent={0}, report_setting_id={1})'.format(cnt, report_setting.id))

if __name__ == '__main__':
    main()
