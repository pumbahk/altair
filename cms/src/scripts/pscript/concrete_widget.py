from pyramid.testing import DummyRequest
from altaircms.front.resources import  PageRenderingResource

url = "sample/page"
request = DummyRequest()
context = PageRenderingResource(request)
request.registry.settings["widget.template_path_format"] = "altaircms:templates/front/widget/%s.mako"
request.matchdict["page_name"] = url

from altaircms.front.views import rendering_page
print rendering_page(context, request)
# from altaircms.front.resources import PageRenderingResource
# context = PageRenderingResource(request)
# page, layout = context.get_page_and_layout(url)
# render_tree = context.get_pagerender_tree(page)
# tmpl = 'altaircms:templates/front/layout/' + str(layout.template_filename)
# from mako.template import Template



