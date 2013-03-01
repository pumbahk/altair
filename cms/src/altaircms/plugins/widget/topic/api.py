from altaircms.page.models import Page
from altaircms.widget.models import Widget
from .models import TopicWidget

def get_topic_widget_pages(request):
    return Page.query.filter(TopicWidget.id==Widget.id,Widget.page_id==Page.id)
get_topic_widget_pages.widget = TopicWidget
