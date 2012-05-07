# -*- coding:utf-8 -*-
def includeme(config):
    config.add_crud("performance", title="performance", model="..models.Performance", form=".forms.PerformanceForm")
    config.add_crud("ticket", title="ticket", model="..models.Ticket", form=".forms.TicketForm")
    config.add_crud("promotion_unit",  title="promotion_unit",  model="..plugins.widget.promotion.models.PromotionUnit",  form=".forms.PromotionUnitForm")
    config.add_crud("promotion",  title="promotion",  model="..plugins.widget.promotion.models.Promotion",  form=".forms.PromotionForm")

