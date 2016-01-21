# -*- coding: utf-8 -*-


def includeme(config):
    from .resources import PrintedReportSettingAdminResource
    config.add_route('printed_reports.edit', '/event/{event_id}', factory=PrintedReportSettingAdminResource)
    config.add_route('printed_reports.report_setting_update', '/event/{event_id}/report_setting_update', factory=PrintedReportSettingAdminResource)
    config.add_route('printed_reports.recipients_update', '/event/{event_id}/recipients_update', factory=PrintedReportSettingAdminResource)
