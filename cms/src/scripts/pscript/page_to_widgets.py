from altaircms.page.models import Page
from altaircms.widget.generate import WidgetTreeProxy
from altaircms.front.generate import get_pagerender_tree


page = Page.query.filter(Page.id==2).one()
# page -> WidgetTree -> PageRenderTree -> ConcreteRenderTree -> render

page = Page.query.filter(Page.id==2).one()
config = {"widget.template_path_format": "altaircms:templates/front/widget/%s.mako"}
print get_pagerender_tree(WidgetTreeProxy(page)).concrete(config=config)
