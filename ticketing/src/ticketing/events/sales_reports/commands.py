# -*- coding: utf-8 -*-

import logging
import os
import sys
from datetime import datetime, timedelta

from paste.util.multidict import MultiDict
from pyramid.paster import bootstrap

logger = logging.getLogger(__name__)

def main(argv=sys.argv):
    from ticketing.core.models import ReportSetting, Mailer, Event, Organization, ReportFrequencyEnum
    from ticketing.operators.models import Operator
    from ticketing.events.sales_reports.forms import SalesReportForm
    from ticketing.events.sales_reports.sendmail import sendmail, get_performance_sales_summary

    if len(sys.argv) < 4:
        print 'ERROR: invalid args %s' % sys.argv
        return

    config_file = argv[1]
    app_env = bootstrap(config_file)

    log_file = os.path.abspath(argv[2])
    logging.config.fileConfig(log_file)
    logger.info('start send_sales_report batch')

    frequency = argv[3]
    if frequency == ReportFrequencyEnum.Daily.k:
        frequency_num = ReportFrequencyEnum.Daily.v
        target = datetime.now() - timedelta(days=1)
        limited_from = target.strftime('%Y-%m-%d 00:00')
        limited_to = target.strftime('%Y-%m-%d 23:59')
    elif frequency == ReportFrequencyEnum.Weekly.k:
        frequency_num = ReportFrequencyEnum.Weekly.v
        target = datetime.now() - timedelta(days=7)
        limited_from = target.strftime('%Y-%m-%d 00:00')
        limited_to = target.strftime('%Y-%m-%d 23:59')
    else:
        logging.error('invalid args %s' % sys.argv)
        return

    report_settings = ReportSetting.query.filter_by(frequency=frequency_num).all()
    for report_setting in report_settings:
        event_id = report_setting.event_id
        event = Event.get(event_id)
        if event is None:
            logging.error('event not found (id=%s)' % event_id)
            continue

        params = dict(
            recipient=report_setting.operator.email,
            limited_from=limited_from,
            limited_to=limited_to
        )
        form = SalesReportForm(MultiDict(params), event_id=event_id)
        if event.sales_end_on < form.limited_from.data or form.limited_to.data < event.sales_start_on:
            continue

        sendmail(event, form)

    logger.info('end send_sales_report batch (sent=%s)' % len(report_settings))

if __name__ == '__main__':
    main()
