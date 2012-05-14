from .models import HeadingWidget

def collect_heading_widgets_from_page(page):
    return HeadingWidget.query.filter(page.id==HeadingWidget.page_id)
