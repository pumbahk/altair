# -*- coding: utf-8 -*-
import api
import forms
from pyramid.httpexceptions import HTTPNotFound
from sqlalchemy.orm.exc import NoResultFound
from altair.app.ticketing.resources import TicketingAdminResource
from altair.app.ticketing.core.models import Event, PrintedReportRecipient


class PrintedReportSettingAdminResource(TicketingAdminResource):
    def __init__(self, request):
        super(PrintedReportSettingAdminResource, self).__init__(request)
        if not self.user:
            raise HTTPNotFound()

        try:
            event_id = long(self.request.matchdict.get('event_id'))
            self.event = Event.query.filter(Event.id == event_id).one()
        except (TypeError, ValueError, NoResultFound):
            raise HTTPNotFound()

        self.printed_report_setting = api.get_or_create_printed_report_setting(request, self.event, self.user)

    def update_printed_report_setting(self):
        form = forms.PrintedReportSettingForm(self.request.POST)
        self.printed_report_setting.start_on = form.start_on.data
        self.printed_report_setting.end_on = form.end_on.data

    def update_recipient(self):
        form = forms.PrintedReportRecipientForm(self.request.POST)
        self.printed_report_setting.recipients = []
        for line in form.recipients.data.splitlines():
            row = line.split(',')
            if len(row) != 2:
                continue
            if not row[0].strip() or not row[1].strip():
                continue

            recipient = PrintedReportRecipient()
            recipient.name = row[0].strip()
            recipient.email = row[1].strip()
            recipient.organization_id = self.printed_report_setting.event.organization_id
            self.printed_report_setting.recipients.append(recipient)

    def get_printed_report_recipients_form(self):
        form = forms.PrintedReportRecipientForm()
        recipient_list = []
        for recipient in self.printed_report_setting.recipients:
            recipient_list.append(recipient.name + "," + recipient.email)
        form.recipients.data = "\n".join(recipient_list)
        return form
