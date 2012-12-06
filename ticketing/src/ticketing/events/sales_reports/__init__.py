# -*- coding: utf-8 -*-

def includeme(config):
    config.add_route('sales_reports.index', '/')
    config.add_route('sales_reports.event','/event/{event_id}')
    config.add_route('sales_reports.performance', '/performance/{performance_id}')
    config.add_route('sales_reports.preview','/preview/{event_id}')
    config.add_route('sales_reports.mail_body','/mail_body/{event_id}')
    config.add_route('sales_reports.send_mail','/send_mail/{event_id}')

    config.add_route('sales_reports.mail.new', '/mail/new/{event_id}')
    config.add_route('sales_reports.mail.delete', '/mail/delete/{report_setting_id}')
