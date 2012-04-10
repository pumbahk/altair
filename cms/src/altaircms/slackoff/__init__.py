# -*- coding:utf-8 -*-
def includeme(config):
    config.add_crud("performance", title="performance", model="..models.Performance", form=".forms.PerformanceForm")
    config.add_crud("ticket", title="ticket", model="..models.Ticket", form=".forms.TicketForm")

