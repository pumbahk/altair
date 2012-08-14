# -*- coding: utf-8 -*-
import logging
import json
import webhelpers.paginate as paginate
from ticketing.fanstatic import with_bootstrap
from pyramid.view import view_config, view_defaults
import sqlalchemy as sa
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPCreated
from pyramid.threadlocal import get_current_registry
from pyramid.url import route_path
from pyramid.response import Response
from pyramid.path import AssetResolver

from ticketing.views import BaseView

from ticketing.core.models import DeliveryMethod
from .models import TicketFormat, Ticket
from . import forms
from . import helpers

@view_defaults(decorator=with_bootstrap, permission="event_editor")
class TicketFormats(BaseView):
    @view_config(route_name='tickets.formats.index', renderer='ticketing:templates/tickets/formats/index.html', request_method="GET")
    def index(self):
        qs = TicketFormat.filter_by(organization_id=self.context.user.organization_id).order_by(sa.desc("updated_at"))
        return dict(h=helpers, formats=qs)

    @view_config(route_name='tickets.formats.index', renderer='ticketing:templates/tickets/formats/index.html', request_method="GET", 
                 request_param="sort")
    def index_with_sortable(self):
        direction = helpers.get_direction(self.request.params["direction"])
        qs = TicketFormat.filter_by(organization_id=self.context.user.organization_id)
        qs = qs.order_by(direction(self.request.params["sort"]))
        return dict(h=helpers, formats=qs)

    @view_config(route_name="tickets.formats.edit",renderer='ticketing:templates/tickets/formats/new.html')
    def edit(self):
        format = TicketFormat.filter_by(organization_id=self.context.user.organization_id,
                                    id=self.request.matchdict["id"]).first()
        if format is None:
            raise HTTPNotFound("this is not found")

        form = forms.TicketFormatForm(organization_id=self.context.user.organization_id, 
                                      name=format.name, 
                                      data_value=json.dumps(format.data), 
                                      delivery_methods=[m.id for m in format.delivery_methods])
        return dict(h=helpers, form=form, format=format)
        
    @view_config(route_name='tickets.formats.edit', renderer='ticketing:templates/tickets/formats/new.html', request_method="POST")
    def edit_post(self):
        format = TicketFormat.filter_by(organization_id=self.context.user.organization_id,
                                    id=self.request.matchdict["id"]).first()
        if format is None:
            raise HTTPNotFound("this is not found")

        form = forms.TicketFormatForm(organization_id=self.context.user.organization_id, 
                                      formdata=self.request.POST)
        if not form.validate():
            return dict(h=helpers, form=form, format=format)
        
        params = form.data
        format.name=params["name"]
        format.data=params["data_value"]

        for dmethod in format.delivery_methods:
            format.delivery_methods.remove(dmethod)
        for dmethod in DeliveryMethod.filter(DeliveryMethod.id.in_(form.data["delivery_methods"])):
            format.delivery_methods.append(dmethod)
        format.save()
        self.request.session.flash(u'チケット様式を更新しました')
        return HTTPFound(location=self.request.route_path("tickets.formats.index"))

    @view_config(route_name='tickets.formats.new', renderer='ticketing:templates/tickets/formats/new.html')
    def new(self):
        ## ugly
        form = forms.TicketFormatForm(organization_id=self.context.user.organization_id, 
                                      data_value=u"""\
{
  "size": {"width": "", "height": ""},
  "perforations": {"vertical": [], "horizontal": []}, 
  "printable_areas": [{"x": "", "y": "", "width": "", "height":""}]
}
""")
        return dict(h=helpers, form=form)

    @view_config(route_name='tickets.formats.new', renderer='ticketing:templates/tickets/formats/new.html', 
                 request_param="id")
    def new_with_baseobject(self):
        format = TicketFormat.filter_by(organization_id=self.context.user.organization_id,
                                    id=self.request.params["id"]).first()
        if format is None:
            raise HTTPNotFound("this is not found")

        form = forms.TicketFormatForm(organization_id=self.context.user.organization_id, 
                                      name=format.name, 
                                      data_value=json.dumps(format.data), 
                                      delivery_methods=[m.id for m in format.delivery_methods])
        return dict(h=helpers, form=form)

    @view_config(route_name='tickets.formats.new', renderer='ticketing:templates/tickets/formats/new.html', request_method="POST")
    def new_post(self):
        form = forms.TicketFormatForm(organization_id=self.context.user.organization_id, 
                                      formdata=self.request.POST)
        if not form.validate():
            return dict(h=helpers, form=form)
        
        params = form.data
        ticket_format = TicketFormat(name=params["name"], 
                                data=params["data_value"], 
                                organization_id=self.context.user.organization_id
                                )

        for dmethod in DeliveryMethod.filter(DeliveryMethod.id.in_(form.data["delivery_methods"])):
            ticket_format.delivery_methods.append(dmethod)
        ticket_format.save()
        self.request.session.flash(u'チケット様式を登録しました')
        return HTTPFound(location=self.request.route_path("tickets.formats.index"))
            

    @view_config(route_name='tickets.formats.delete', request_method="POST")
    def delete_post(self):
        format = TicketFormat.filter_by(organization_id=self.context.user.organization_id,
                                    id=self.request.matchdict["id"]).first()
        if format is None:
            raise HTTPNotFound("this is not found")

        format.delete()
        self.request.session.flash(u'チケット様式を削除しました')

        return HTTPFound(location=self.request.route_path("tickets.formats.index"))

    @view_config(route_name='tickets.formats.show', renderer='ticketing:templates/tickets/formats/show.html')
    def show(self):
        qs = TicketFormat.query.filter_by(id=self.request.matchdict['id'])
        format = qs.filter_by(organization_id=self.context.user.organization_id).one()
        return dict(h=helpers, format=format)
    

@view_defaults(decorator=with_bootstrap, permission="event_editor")
class TicketTemplates(BaseView):
    @view_config(route_name='tickets.templates.index', renderer='ticketing:templates/tickets/templates/index.html')
    def index(self):
        pass 
