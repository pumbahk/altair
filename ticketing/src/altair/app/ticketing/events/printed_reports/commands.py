# -*- coding: utf-8 -*-
import logging
import sys
import argparse
from sqlalchemy import or_
import traceback
from datetime import datetime, time, timedelta
from sqlalchemy.sql import func
from altair.app.ticketing.orders.models import Order, OrderedProduct, OrderedProductItem, OrderedProductItemToken
from pyramid.renderers import render_to_response
from pyramid.paster import bootstrap, setup_logging
from altair.app.ticketing.models import DBSession
from altair import multilock
import transaction
from altair.app.ticketing.core.models import PrintedReportSetting, PrinttedReportSetting_PrintedReportRecipient, PrintedReportRecipient
from altair.app.ticketing.events.sales_reports.reports import sendmail


logger = logging.getLogger(__name__)


def main(argv=sys.argv):
    try:

        parser = argparse.ArgumentParser()
        parser.add_argument('config')
        args = parser.parse_args()

        setup_logging(args.config)
        env = bootstrap(args.config)
        registry = env['registry']

        with multilock.MultiStartLock('send_printed_reports'):

            logger.info('start send_printed_report batch')

            now = datetime.now().replace(second=0)
            settings = registry.settings

            session = DBSession

            today = datetime.now()
            yesterday = today - timedelta(days=1)

            midnight = datetime.strptime("{0.year}-{0.month}-{0.day} 00:00:00".format(today), '%Y-%m-%d %H:%M:%S')

            report_settings_ids = [setting.id for setting in session.query(PrintedReportSetting) \
                .join(PrinttedReportSetting_PrintedReportRecipient,
                      PrinttedReportSetting_PrintedReportRecipient.report_setting_id == PrintedReportSetting.id) \
                .join(PrintedReportRecipient, PrintedReportRecipient.id == PrinttedReportSetting_PrintedReportRecipient.report_recipient_id)
                .filter(
                    or_( \
                        PrintedReportSetting.last_sent_at == None, \
                        PrintedReportSetting.last_sent_at <= midnight \
                    )
                ) \
                .filter(PrintedReportSetting.start_on <= now) \
                .filter(PrintedReportSetting.end_on > now).all()]

            for cnt, report_setting_id in enumerate(report_settings_ids):
                report_setting = session.query(PrintedReportSetting).filter(
                    PrintedReportSetting.id == report_setting_id).first()

                # 指定時刻が指定されていない場合は、日付が変わったら送る
                if report_setting.time:
                    today_time = time(today.hour, today.minute, today.second)
                    if report_setting.time > today_time:
                        logger.info('printed_report_setting_id: {0}, It isn\'t the transmission time.'.format(report_setting.id))
                        continue

                logger.info('printed_report_setting_id: {0}'.format(report_setting.id))
                report_setting.last_sent_at = today

                date_format = '%Y-%m-%d 00:00'
                period = u"{0} - {1}".format(yesterday.strftime(date_format), today.strftime(date_format))

                event = report_setting.event
                performance_printed_num = {}

                if not event:
                    # 紐付いているイベントが削除されている
                    logger.info('printed_report_setting_id: {0}, Event has been deleted.'.format(report_setting.id))
                    continue

                try:
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
                except RuntimeError as e:
                    logging.error("RuntimeError: {0}. PrintedReportSettingID = {1}".format(e.message, report_setting.id))
                except Exception as e:
                    logging.error("printed report failed. report_setting_id = {}, error: {}({})".format(report_setting.id, type(e), e.message))

                logger.info('end send_printed_report batch (sent={0}, report_setting_id={1})'.format(cnt, report_setting.id))

                transaction.commit()

    except multilock.AlreadyStartUpError as err:
        logger.warn('{}'.format(repr(err)))


if __name__ == '__main__':
    main()
