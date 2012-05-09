# -*- coding:utf-8 -*-
def includeme(config):
    config.add_crud("performance", title="performance", model="..models.Performance",
                    form=".forms.PerformanceForm", mapper=".mappers.performance_mapper")
    config.add_crud("ticket", title="ticket", model="..models.Ticket", 
                    form=".forms.TicketForm", mapper=".mappers.ticket_mapper")
    config.add_crud("promotion_unit",  title="promotion_unit",  model="..plugins.widget.promotion.models.PromotionUnit", 
                    form=".forms.PromotionUnitForm",  mapper=".mappers.promotion_unit_mapper")
    config.add_crud("promotion",  title="promotion",  model="..plugins.widget.promotion.models.Promotion",  form=".forms.PromotionForm")

    config.add_crud("category", title="category", model="..models.Category", form=".forms.CategoryForm")

