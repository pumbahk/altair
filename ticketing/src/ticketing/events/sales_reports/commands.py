from ticketing.logicaldeleting import install as install_ld
install_ld()
import logging
import os
import sys
from os.path import abspath, dirname
sys.path.append(abspath(dirname(dirname(__file__))))

from pyramid.paster import bootstrap
from pyramid.renderers import render_to_response
from ticketing.core.models import ReportSetting, Mailer, Event, Organization
from ticketing.operators.models import Operator
from ticketing.events.sales_reports.forms import SalesReportForm
from ticketing.events.sales_reports.sendmail import sendmail, get_performance_sales_summary

logger = logging.getLogger(__name__)

logging.basicConfig()

def get_settings(frequency_num):
    return ReportSetting.query.filter(ReportSetting.frequency==frequency_num)\
        .with_entities(ReportSetting.event_id, ReportSetting.operator_id).all()

def main(argv=sys.argv):
    config_file = argv[1]
    # configuration
    if config_file is None:
        print 'You must give a config file'
        return

    log_file = os.path.abspath(argv[2])
    frequency = argv[3]
    if frequency == "Daily":
        frequency_num = 1
    elif frequency == "Weekly":
        frequency_num = 2
    else:
        logging.error(e.message)

    logging.config.fileConfig(log_file)
    app_env = bootstrap(config_file)
    registry = app_env['registry']
    settings = registry.settings

    # send mail magazine
    report = []
    for report_setting in get_settings(frequency_num):
        event_id = report_setting.event_id
        event = Event.get(event_id)
        if event is None:
            logging.error(e.message)

        performances_reports = {}
        form = SalesReportForm(event_id=event_id)
        event_product = get_performance_sales_summary(form,event.organization)
        mailer = sendmail(event, form, report_setting.operator_id);

 

if __name__ == '__main__':
    main()
