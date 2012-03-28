from pyramid.view import view_config
from pyramid.renderers import render_to_response

class ReuseWidgetView(object):
    def __init__(self, request):
        self.request = request

    def _create_or_update(self):
        data = self.request.json_body["data"]
        page_id = self.request.json_body["page_id"]
        context = self.request.context
        widget = context.get_widget(self.request.json_body.get("pk"))
        widget = context.update_data(widget,
                                     page_id=page_id, 
                                     **data)
        context.add(widget, flush=True)
        r = self.request.json_body.copy()
        r.update(pk=widget.id)
        return r

    @view_config(route_name="reuse_widget_create", renderer="json", request_method="POST")
    def create(self):
        return self._create_or_update()

    @view_config(route_name="reuse_widget_update", renderer="json", request_method="POST")
    def update(self):
        return self._create_or_update()

    @view_config(route_name="reuse_widget_delete", renderer="json", request_method="POST")
    def delete(self):
        context = self.request.context
        widget = context.get_widget(self.request.json_body["pk"])
        context.delete(widget, flush=True)
        return {"status": "ok"}

    @view_config(route_name="reuse_widget_dialog", renderer="altaircms.plugins.widget:reuse/dialog.mako", request_method="GET")
    def dialog(self):
        context = self.request.context
        widget = context.get_widget(self.request.GET.get("pk"))
        form = forms.CountDownChoiceForm(**widget.to_dict())
        return {"form": form}

def rendering_source_page(request):
    page = request._reuse_widget.source_page
    from altaircms.front.resources import PageRenderingResource
    rendering_context = PageRenderingResource(request)
    layout = page.layout

    block_context = rendering_context.get_block_context(page)
    block_context.scan(request=request,
                       page=page, 
                       performances=rendering_context.get_performances(page),
                       tickets=rendering_context.get_tickets(page), 
                       event=page.event)
    tmpl = rendering_context.get_layout_template(layout, rendering_context.get_render_config())
    params = dict(page=page, display_blocks=block_context.blocks)
    return render_to_response(tmpl, params, request)
