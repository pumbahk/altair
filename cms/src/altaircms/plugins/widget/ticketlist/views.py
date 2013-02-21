# -*- coding:utf-8 -*-
from pyramid.view import view_config, view_defaults
from altaircms.auth.api import require_login, get_or_404
from altaircms.page.models import Page
from altaircms.models import SalesSegment
import sqlalchemy.orm as orm
from . import forms
import logging
logger = logging.getLogger(__name__)
from webob.multidict import MultiDict

from pyramid.response import Response
def as_postdata(request):
    return MultiDict(request.json_body["data"])

@view_defaults(custom_predicates=(require_login,))
class TicketlistWidgetView(object):
    def __init__(self, request):
        self.request = request

    def _create_or_update(self):
        try:
            page_id = self.request.json_body["page_id"]
            form = forms.TicketlistChoiceForm(as_postdata(self.request))
            page = get_or_404(self.request.allowable(Page), Page.id==page_id)

            form.configure(self.request, page)
            if not form.validate():
                logger.warn(str(form.errors))
                return {}

            context = self.request.context
            widget = context.get_widget(self.request.json_body.get("pk"))
            widget = context.update_data(widget,
                                         page_id=page_id, 
                                         **(form.data))
            context.add(widget, flush=True)
            r = self.request.json_body.copy()
            r.update(pk=widget.id)
            return r
        except Exception, e:
            logger.error(str(e))
            return {}

    @view_config(route_name="ticketlist_widget_create", renderer="json", request_method="POST")
    def create(self):
        return self._create_or_update()

    @view_config(route_name="ticketlist_widget_update", renderer="json", request_method="POST")
    def update(self):
        return self._create_or_update()

    @view_config(route_name="ticketlist_widget_delete", renderer="json", request_method="POST")
    def delete(self):
        context = self.request.context
        widget = context.get_widget(self.request.json_body["pk"])
        context.delete(widget, flush=True)
        return {"status": "ok"}

    @view_config(route_name="ticketlist_widget_dialog", renderer="altaircms.plugins.widget:ticketlist/dialog.html", request_method="GET")
    def dialog(self):
        context = self.request.context
        widget = context.get_widget(self.request.GET.get("pk"))
        page = get_or_404(self.request.allowable(Page), Page.id==self.request.GET["page_id"])
        self.request.event_id = page.event_id
        form = forms.TicketlistChoiceForm(**widget.to_dict())
        form.configure(self.request, page)
        return {"widget": widget, "form": form}

@view_config(route_name="api.combobox.salessegment", renderer="string")
def api_combobox_salessegment_from_performance(context, request):
    try:
        form = forms.TicketChoiceForm()
        form.configure(request)
        return Response(form.target_salessegment_id.__html__())
    except Exception, e:
            logger.error(str(e))
            return Response("")
        
