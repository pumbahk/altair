# -*- coding: utf-8 -*-
from altair.app.ticketing.core.models import PrintedReportSetting
from datetime import datetime


def get_or_create_printed_report_setting(request, event, operator):
    printed_report_setting = PrintedReportSetting.query.filter_by(event_id=event.id).first()
    if not printed_report_setting:
        printed_report_setting = PrintedReportSetting()
        printed_report_setting.event_id = event.id
        printed_report_setting.operator_id = operator.id
        printed_report_setting.start_on = datetime.now()
        printed_report_setting.end_on = datetime.now()
        printed_report_setting.save()
    return printed_report_setting
