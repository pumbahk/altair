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

from altair.app.ticketing.events.sales_reports.reports import EventReporter, PerformanceReporter

logger = logging.getLogger(__name__)

def main(argv=sys.argv):
    from altair.app.ticketing.core.models import ReportSetting,\
        ReportFrequencyEnum, ReportPeriodEnum, Organization, Event
    from altair.app.ticketing.events.sales_reports.forms import SalesReportForm
    from altair.app.ticketing.events.sales_reports.reports import sendmail

    if len(sys.argv) < 3:
        print 'ERROR: invalid args %s' % sys.argv
        return

    log_file = os.path.abspath(argv[2])
    logging.config.fileConfig(log_file)

    config_file = argv[1]
    app_env = bootstrap(config_file)
    request = app_env['request']

    logger.info('start send_sales_report batch')

    now = datetime.now().replace(minute=0, second=0)
    settings = get_current_registry().settings

    query = ReportSetting.query.filter(and_(
        ReportSetting.time==now.hour,
        or_(ReportSetting.start_on==None, ReportSetting.start_on<now),
        or_(ReportSetting.end_on==None, ReportSetting.end_on>now),
        or_(ReportSetting.day_of_week==None, ReportSetting.day_of_week==now.isoweekday())
    ))

    i = 0
    reports = {}
    for report_setting in query.all():
        logger.info('report_setting_id: %s' % report_setting.id)

        from_date = now
        to_date = now
        limited_from = None
        limited_to = None
        need_total = True
        if report_setting.period == ReportPeriodEnum.Entire.v[0]:
            need_total = False
            limited_to = to_date.strftime('%Y-%m-%d %H:%M')
        elif report_setting.period == ReportPeriodEnum.Normal.v[0]:
            to_date = now - timedelta(days=1)
            limited_to = to_date.strftime('%Y-%m-%d 23:59')

        if report_setting.frequency == ReportFrequencyEnum.Daily.v[0]:
            from_date = to_date
        elif report_setting.frequency == ReportFrequencyEnum.Weekly.v[0]:
            from_date = now - timedelta(days=7)
        if report_setting.period == ReportPeriodEnum.Normal.v[0]:
            limited_from = from_date.strftime('%Y-%m-%d 00:00')

        event = report_setting.event
        performance = report_setting.performance
        params = dict(
            event_id=report_setting.event_id,
            performance_id=report_setting.performance_id,
        )
        if limited_from:
            params.update(dict(limited_from=limited_from))
        if limited_to:
            params.update(dict(limited_to=limited_to))
        form = SalesReportForm(MultiDict(params))
        form.need_total.data = need_total

        if performance:
            end_on = performance.end_on or performance.start_on
            if end_on < now:
                continue

            if form not in reports:
                reporter = PerformanceReporter(request, form, performance)
                if not reporter.reporters:
                    continue
                render_param = dict(performance_reporter=reporter)
                reports[form] = render_to_response('altair.app.ticketing:templates/sales_reports/performance_mail.html', render_param)
            subject = u'%s (開催日:%s)' % (performance.name, performance.start_on.strftime('%Y-%m-%d %H:%M'))
            _event = Event.get(id=performance.event_id)
            organization = Organization.get(id=_event.organization_id)
        elif event:
            # 販売終了日の翌日まで自動レポートの送信対象に含める
            sales_end_on = None
            if event.sales_end_on:
                sales_end_on = event.sales_end_on + timedelta(days=1)
            final_end_on = None
            if event.final_performance:
                final_end_on = event.final_performance.end_on or event.final_performance.start_on
            if (from_date and sales_end_on and sales_end_on < from_date) or\
               (from_date and final_end_on and final_end_on < from_date) or\
               (form.limited_to.data and form.limited_to.data < event.sales_start_on):
                logger.info('continue(not in term)')
                logger.info('from_date=%s, sales_end_on=%s, final_end_on=%s, form.limited_to.data=%s, event.sales_start_on=%s'
                    % (from_date, sales_end_on, final_end_on, form.limited_to.data, event.sales_start_on))
                continue

            if form not in reports:
                reporter = EventReporter(request, form, event)
                if not reporter.reporters:
                    logger.info('continue(no report)')
                    continue
                render_param = dict(event_reporter=reporter)
                reports[form] = render_to_response('altair.app.ticketing:templates/sales_reports/event_mail.html', render_param)
            subject = event.title
            organization = Organization.get(id=event.organization_id)
        else:
            logging.error('event/performance not found (report_setting_id=%s)' % report_setting.id)
            continue

        sendmail(settings, report_setting.recipient, u'[売上レポート|%s] %s' % (organization.name, subject), reports[form])
        i += 1

    logger.info('end send_sales_report batch (sent=%s)' % i)

if __name__ == '__main__':
    main()
