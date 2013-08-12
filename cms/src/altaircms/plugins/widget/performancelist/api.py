from altaircms.plugins.api import get_widget_utility
from altaircms.plugins.extra.api import get_stockstatus_summary

def get_stock_data(request, event, widget):
    page = widget.page
    utility = get_widget_utility(request, page, widget.type)
    status_impl = utility.status_impl
    stock_status = get_stockstatus_summary(request, event, status_impl)
    return stock_status
