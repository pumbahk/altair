from altaircms.page.models import Page
from altaircms.widget.generate import WidgetTreeProxy
from altaircms.front.generate import get_page_node_from_page

page = Page.query.filter(Page.id==2).one()
config = dict(widget_file_format="altaircms:templates/front/widget/%s.mako")
print get_page_node_from_page(WidgetTreeProxy(page)).concrete(
    config=config
    )
