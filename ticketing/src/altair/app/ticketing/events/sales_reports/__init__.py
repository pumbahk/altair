# -*- coding: utf-8 -*-

def includeme(config):
    from .resources import SalesReportAdminResource
    config.add_route('sales_reports.index', '/', factory=SalesReportAdminResource)
    config.add_route('sales_reports.event','/event/{event_id}', factory=SalesReportAdminResource)
    config.add_route('sales_reports.performance', '/performance/{performance_id}', factory=SalesReportAdminResource)
    config.add_route('sales_reports.preview','/preview/', factory=SalesReportAdminResource)
    config.add_route('sales_reports.mail_body','/mail_body/', factory=SalesReportAdminResource)
    config.add_route('sales_reports.export','/export/', factory=SalesReportAdminResource)
    config.add_route('sales_reports.export_xml','/export_xml/', factory=SalesReportAdminResource)
    config.add_route('sales_reports.send_mail','/send_mail/', factory=SalesReportAdminResource)

    from .resources import ReportSettingAdminResource
    config.add_route('report_settings.new', '/report_settings/new/', factory=ReportSettingAdminResource)
    config.add_route('report_settings.edit', '/report_settings/edit/{report_setting_id}', factory=ReportSettingAdminResource)
    config.add_route('report_settings.delete', '/report_settings/delete/{report_setting_id}', factory=ReportSettingAdminResource)
