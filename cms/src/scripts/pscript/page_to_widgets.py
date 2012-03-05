from altaircms.page.models import Page
from altaircms.widget.generate import WidgetTreeProxy
from altaircms.widget.tree.genpage import get_pagerender_tree


# page -> WidgetTree -> PageRenderTree -> ConcreteRenderTree -> render
page = Page.query.filter(Page.id==1).one()
config = {"widget.template_path_format": "altaircms:templates/front/widget/%s.mako"}
print get_pagerender_tree(WidgetTreeProxy(page)).concrete(config=config)
