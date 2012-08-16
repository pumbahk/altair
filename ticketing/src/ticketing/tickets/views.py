# -*- coding: utf-8 -*-
import logging
from StringIO import StringIO
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
from ticketing.core.models import TicketFormat, Ticket
from . import forms
from . import helpers
from .response import FileLikeResponse
from .convert import to_opcodes
from lxml import etree

@view_defaults(decorator=with_bootstrap, permission="event_editor")
class TicketFormats(BaseView):
    @view_config(route_name='tickets.formats.index', renderer='ticketing:templates/tickets/formats/index.html', request_method="GET")
    def index(self):
        qs = TicketFormat.filter_by(organization_id=self.context.user.organization_id).order_by(sa.desc("updated_at"))
        return dict(h=helpers, formats=qs)

    # ## todo pagination
    # @view_config(route_name='tickets.formats.index', renderer='ticketing:templates/tickets/formats/index.html', request_method="GET")
    # def index(self):
    #     items_per_page = 3
    #     qs = TicketFormat.filter_by(organization_id=self.context.user.organization_id).order_by(sa.desc("updated_at"))
    #     qs = paginate.Page(qs,
    #                        items_per_page=items_per_page, 
    #                        item_count=qs.count(), 
    #                        url=paginate.PageURL_WebOb(self.request)
    #                        )
    #     if hasattr(self.request.GET, "page"):
    #         n = (int(self.request.GET["page"])-1)*items_per_page
    #         qs = qs.offset(n).limit(items_per_page)
    #     return dict(h=helpers, formats=qs)

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
        qs = TicketFormat.filter_by(id=self.request.matchdict['id'])
        format = qs.filter_by(organization_id=self.context.user.organization_id).one()
        return dict(h=helpers, format=format)

    @view_config(route_name='tickets.formats.data', renderer='json')
    def data(self):
        qs = TicketFormat.filter_by(id=self.request.matchdict['id'])
        format = qs.filter_by(organization_id=self.context.user.organization_id).one()
        return format.data

@view_defaults(decorator=with_bootstrap, permission="event_editor")
class TicketTemplates(BaseView):
    @view_config(route_name='tickets.templates.index', renderer='ticketing:templates/tickets/templates/index.html')
    def index(self):
        qs = Ticket.templates_query().filter_by(organization_id=self.context.user.organization_id)
        return dict(h=helpers, templates=qs)

    @view_config(route_name='tickets.templates.index', renderer='ticketing:templates/tickets/templates/index.html', request_method="GET", 
                 request_param="sort")
    def index_with_sortable(self):
        direction = helpers.get_direction(self.request.params["direction"])
        qs = Ticket.templates_query().filter_by(organization_id=self.context.user.organization_id)
        qs = qs.order_by(direction(self.request.params["sort"]))
        return dict(h=helpers, templates=qs)

    @view_config(route_name="tickets.templates.new", renderer="ticketing:templates/tickets/templates/new.html", 
                 request_method="GET")
    def new(self):
        form = forms.TicketTemplateForm(organization_id=self.context.user.organization_id)
        return dict(h=helpers, form=form)

    @view_config(route_name='tickets.templates.new', renderer='ticketing:templates/tickets/templates/new.html', request_method="POST")
    def new_post(self):
        form = forms.TicketTemplateForm(organization_id=self.context.user.organization_id, 
                                      formdata=self.request.POST)
        if not form.validate():
            return dict(h=helpers, form=form)

        ticket_template = Ticket(name=form.data["name"], 
                                 ticket_format_id=form.data["ticket_format"], 
                                 data=form.data_value, 
                                 organization_id=self.context.user.organization_id
                                 )
        
        ticket_template.save()
        self.request.session.flash(u'チケットテンプレートを登録しました')
        return HTTPFound(location=self.request.route_path("tickets.templates.index"))

    @view_config(route_name='tickets.templates.edit', renderer='ticketing:templates/tickets/templates/new.html',
                 request_method="GET")
    def edit(self):
        template = Ticket.templates_query().filter_by(
            organization_id=self.context.user.organization_id,
            id=self.request.matchdict["id"]).first()

        if template is None:
            raise HTTPNotFound("this is not found")
        
        form = forms.TicketTemplateEditForm(
            organization_id=self.request.context.user.organization_id, 
            name=template.name, 
            ticket_format=template.ticket_format_id
            )
        return dict(h=helpers, form=form, template=template)

    @view_config(route_name='tickets.templates.edit', renderer='ticketing:templates/tickets/templates/new.html',
                 request_method="POST")
    def edit_post(self):
        template = Ticket.templates_query().filter_by(
            organization_id=self.context.user.organization_id,
            id=self.request.matchdict["id"]).first()

        if template is None:
            raise HTTPNotFound("this is not found")

        form = forms.TicketTemplateEditForm(organization_id=self.context.user.organization_id, 
                                        formdata=self.request.POST)
        if not form.validate():
            return dict(h=helpers, form=form, template=template)

        template.name = form.data["name"]
        template.ticket_format_id = form.data["ticket_format"]

        if form.data_value:
            template.data = form.data_value
        template.save()
        self.request.session.flash(u'チケットテンプレートを更新しました')
        return HTTPFound(location=self.request.route_path("tickets.templates.index"))


    @view_config(route_name='tickets.templates.delete', request_method="POST")
    def delete_post(self):
        template = Ticket.templates_query().filter_by(
            organization_id=self.context.user.organization_id,
            id=self.request.matchdict["id"]).first()

        if template is None:
            raise HTTPNotFound("this is not found")

        template.delete()
        self.request.session.flash(u'チケットテンプレートを削除しました')

        return HTTPFound(location=self.request.route_path("tickets.templates.index"))

    @view_config(route_name='tickets.templates.show', renderer='ticketing:templates/tickets/templates/show.html')
    def show(self):
        qs = Ticket.templates_query().filter_by(id=self.request.matchdict['id'])
        template = qs.filter_by(organization_id=self.context.user.organization_id).one()
        return dict(h=helpers, template=template)

    @view_config(route_name='tickets.templates.download')
    def download(self):
        qs = Ticket.templates_query().filter_by(id=self.request.matchdict['id'])
        template = qs.filter_by(organization_id=self.context.user.organization_id).one()
        return FileLikeResponse(StringIO(template.data["drawing"]),
                                request=self.request)

    @view_config(route_name='tickets.templates.data', renderer='json')
    def data(self):
        qs = Ticket.templates_query().filter_by(id=self.request.matchdict['id'])
        template = qs.filter_by(organization_id=self.context.user.organization_id).one()
        data = dict(template.ticket_format.data)
        data.update(dict(drawing=' '.join(to_opcodes(etree.ElementTree(etree.fromstring(template.data['drawing']))))))
        return data

