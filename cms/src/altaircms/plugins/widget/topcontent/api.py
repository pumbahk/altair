from altaircms.page.models import Page
from altaircms.widget.models import Widget
from .models import TopcontentWidget

def get_topcontent_widget_pages(request):
    return Page.query.filter(TopcontentWidget.id==Widget.id,Widget.page_id==Page.id)
get_topcontent_widget_pages.widget = TopcontentWidget
