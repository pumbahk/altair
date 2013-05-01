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

from ticketing.events.sales_reports.reports import EventReporter, PerformanceReporter

logger = logging.getLogger(__name__)

def main(argv=sys.argv):
    from ticketing.core.models import ReportSetting, ReportFrequencyEnum
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
        ReportSetting.time==now.hour,
        or_(ReportSetting.start_on==None, ReportSetting.start_on<now),
        or_(ReportSetting.end_on==None, ReportSetting.end_on>now),
    ))
    if frequency == ReportFrequencyEnum.Weekly.k:
        query = query.filter(ReportSetting.day_of_week==now.isoweekday())

    i = 0
    for report_setting in query.all():
        event = report_setting.event
        performance = report_setting.performance
        params = dict(
            event_id=report_setting.event_id,
            performance_id=report_setting.performance_id,
            recipient=report_setting.recipient,
            limited_from=limited_from,
            limited_to=limited_to
        )
        form = SalesReportForm(MultiDict(params))

        if performance:
            end_on = performance.end_on or performance.start_on
            if end_on < now:
                continue
            logger.info('report_setting_id: %s, performance_id: %s' % (report_setting.id, performance.id))

            if performance not in reports:
                render_param = {
                    'performance_reporter':PerformanceReporter(form, performance)
                }
                reports[performance] = render_to_response('ticketing:templates/sales_reports/performance_mail.html', render_param)
            html = reports[performance]
            subject = u'%s (開催日:%s)' % (performance.name, performance.start_on.strftime('%Y-%m-%d %H:%M'))
        elif event:
            if event.sales_end_on < form.limited_from.data or form.limited_to.data < event.sales_start_on:
                continue
            logger.info('report_setting_id: %s, event_id: %s' % (report_setting.id, event.id))

            if event not in reports:
                render_param = {
                    'event_reporter':EventReporter(form, event),
                }
                reports[event] = render_to_response('ticketing:templates/sales_reports/event_mail.html', render_param)
            html = reports[event]
            subject = event.title
        else:
            logging.error('event/performance not found (report_setting_id=%s)' % report_setting.id)
            continue

        subject = u'[売上レポート] %s' % subject
        sendmail(settings, report_setting.recipient, subject, html)
        i += 1

    logger.info('end send_sales_report batch (sent=%s)' % i)

if __name__ == '__main__':
    main()
