from ticketing.logicaldeleting import install as install_ld
install_ld()

import csv
import optparse
import os
import sys
from os.path import abspath, dirname
sys.path.append(abspath(dirname(dirname(__file__))))

from pyramid.paster import bootstrap
from pyramid.renderers import render_to_response
from ticketing.core.models import ReportSetting, Mailer, session, Event, Organization
from ticketing.operators.models import Operator
from ticketing.events.sales_reports.views import SalesReports
from ticketing.events.sales_reports.forms import SalesReportForm
import logging
logging.basicConfig()

class Context(object):
    pass

def main(argv=sys.argv):
    config_file = sys.argv[1]
    # configuration
    if config_file is None:
        print 'You must give a config file'
        return

    log_file = os.path.abspath(sys.argv[2])
    frequency = sys.argv[3]
    if frequency == "Daily":
        frequency_num = 1
    elif frequency == "Weekly":
        frequency_num = 2
    logging.config.fileConfig(log_file)
    app_env = bootstrap(config_file)
    registry = app_env['registry']
    settings = registry.settings

    sales_reports = SalesReports(context=None, request=None)

    # send mail magazine
    report = []
    for report_setting in ReportSetting.get_reservations(frequency_num):
        event_id = report_setting.event_id
        print 'event_id=%s' % event_id
        event = Event.get(event_id)
        if event is None:
            raise HTTPNotFound('event id %d is not found' % event_id)

        context = Context()
        setattr(context, 'organization', event.organization)
        sales_reports.context = context
        performances_reports = {}
        sales_reports.form = SalesReportForm(event_id=event_id)
        event_product = sales_reports._get_performance_sales_summary(sales_reports.form)

        for performance in event.performances:
            print 'performance_id=%s' % performance.id
            report_by_sales_segment = {}
            for sales_segment in event.sales_segments:
                print 'sales_segment_id=%s' % sales_segment.id
                sales_report_form = SalesReportForm(performance_id=performance.id, sales_segment_id=sales_segment.id)
                report_by_sales_segment[sales_segment.name] = sales_reports._get_performance_sales_summary(sales_report_form)
            performances_reports[performance.id] = dict(
                performance=performance,
                report_by_sales_segment=report_by_sales_segment
            )

        render_param = {
            'event_product':event_product,
            'form':sales_reports.form,
            'performances_reports':performances_reports
        }

        sender = settings['mail.message.sender']
        operator = Operator.get(report_setting.operator_id)
        recipient = 'ribontolili@gmail.com' #operator
        subject = event.title
        print 'create html'
        html = render_to_response('ticketing:templates/sales_reports/mail_body.html', render_param, request=sales_reports.request)
        print 'create html done'
        mailer = Mailer(settings)
        mailer.create_message(
            sender = sender,
            recipient = recipient,
            subject = subject,
            body = '',
            html = html.text
        )

        try:
            mailer.send(sender, recipient.split(','))
        except Exception, e:
            logging.error(e.message)

    print 'success'


if __name__ == '__main__':
    main()
