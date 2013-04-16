# -*- coding: utf-8 -*-

import logging
import os
import sys
from datetime import datetime, timedelta
from paste.util.multidict import MultiDict
from pyramid.threadlocal import get_current_registry
from pyramid.renderers import render_to_response
from pyramid.paster import bootstrap
from sqlalchemy import or_, and_

from ticketing.events.sales_reports.reports import EventReporter

logger = logging.getLogger(__name__)

def main(argv=sys.argv):
    from ticketing.core.models import ReportSetting, Event, ReportFrequencyEnum
    from ticketing.events.sales_reports.forms import SalesReportForm
    from ticketing.events.sales_reports.reports import sendmail

    if len(sys.argv) < 4:
        print 'ERROR: invalid args %s' % sys.argv
        return

    config_file = argv[1]
    app_env = bootstrap(config_file)

    log_file = os.path.abspath(argv[2])
    logging.config.fileConfig(log_file)
    logger.info('start send_sales_report batch')

    now = datetime.now().replace(minute=0, second=0)
    frequency = argv[3]
    if frequency == ReportFrequencyEnum.Daily.k:
        frequency_num = ReportFrequencyEnum.Daily.v[0]
        target = now - timedelta(days=1)
        limited_from = target.strftime('%Y-%m-%d 00:00')
        limited_to = target.strftime('%Y-%m-%d 23:59')
    elif frequency == ReportFrequencyEnum.Weekly.k:
        frequency_num = ReportFrequencyEnum.Weekly.v[0]
        target = now - timedelta(days=7)
        limited_from = target.strftime('%Y-%m-%d 00:00')
        target = now - timedelta(days=1)
        limited_to = target.strftime('%Y-%m-%d 23:59')
    else:
        logging.error('invalid args %s' % sys.argv)
        return

    reports = {}
    settings = get_current_registry().settings
    query = ReportSetting.query.filter(and_(
        ReportSetting.frequency==frequency_num,
        ReportSetting.time==now.strftime('%H'),
        or_(ReportSetting.start_on==None, ReportSetting.start_on<now),
        or_(ReportSetting.end_on==None, ReportSetting.end_on>now),
    ))
    if frequency == ReportFrequencyEnum.Weekly.k:
        query = query.filter(ReportSetting.day_of_week==now.weekday())

    i = 0
    for i, report_setting in enumerate(query.all()):
        event_id = report_setting.event_id
        event = Event.get(event_id)
        if event is None:
            logging.error('event not found (id=%s)' % event_id)
            continue

        params = dict(
            recipient=report_setting.recipient,
            limited_from=limited_from,
            limited_to=limited_to
        )
        form = SalesReportForm(MultiDict(params), event_id=event_id)
        if event.sales_end_on < form.limited_from.data or form.limited_to.data < event.sales_start_on:
            continue

        logger.info('report_setting_id: %sl, event_id: %s' % (report_setting.id, event_id))

        if event_id not in reports:
            render_param = {
                'event_reporter':EventReporter(form, event),
            }
            reports[event_id] = render_to_response('ticketing:templates/sales_reports/mail_body.html', render_param)
        subject = form.subject.data or u'[売上レポート] %s' % event.title
        html = reports[event_id]
        sendmail(settings, form.recipient.data, subject, html)

    logger.info('end send_sales_report batch (sent=%s)' % i)

if __name__ == '__main__':
    main()
