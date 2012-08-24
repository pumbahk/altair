# -*- coding: utf-8 -*-
import logging
from StringIO import StringIO
import json
import webhelpers.paginate as paginate
import sqlalchemy as sa
from ticketing.fanstatic import with_bootstrap
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound

from ticketing.views import BaseView

from ticketing.core.models import DeliveryMethod
from ticketing.core.models import TicketFormat, Ticket
from ticketing.core.models import TicketPrintQueue
from . import forms
from . import helpers
from .response import FileLikeResponse
from .convert import to_opcodes
from lxml import etree



@view_defaults(decorator=with_bootstrap, permission="event_editor")
class TicketMasters(BaseView):
    @view_config(route_name='tickets.index', renderer='ticketing:templates/tickets/index.html', request_method="GET")
    def index(self):
        ticket_format_sort_by, ticket_format_direction = helpers.sortparams('ticket_format', self.request, ('updated_at', 'desc'))

        ticket_template_sort_by, ticket_template_direction = helpers.sortparams('ticket_template', self.request, ('updated_at', 'desc'))

        ticket_format_qs = TicketFormat.filter_by(organization_id=self.context.user.organization_id)
        ticket_template_qs = Ticket.templates_query().filter_by(organization_id=self.context.user.organization_id)

        ticket_format_qs = ticket_format_qs.order_by(helpers.get_direction(ticket_format_direction)(ticket_format_sort_by))

        ticket_template_qs = ticket_template_qs.order_by(helpers.get_direction(ticket_template_direction)(ticket_template_sort_by))
        return dict(h=helpers, formats=ticket_format_qs, templates=ticket_template_qs)

@view_defaults(decorator=with_bootstrap, permission="event_editor")
class TicketFormats(BaseView):
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
        return HTTPFound(location=self.request.route_path("tickets.index"))

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
        return HTTPFound(location=self.request.route_path("tickets.index"))
            

    @view_config(route_name='tickets.formats.delete', request_method="POST")
    def delete_post(self):
        format = TicketFormat.filter_by(organization_id=self.context.user.organization_id,
                                    id=self.request.matchdict["id"]).first()
        if format is None:
            raise HTTPNotFound("this is not found")

        format.delete()
        self.request.session.flash(u'チケット様式を削除しました')

        return HTTPFound(location=self.request.route_path("tickets.index"))

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
        return HTTPFound(location=self.request.route_path("tickets.index"))

    @view_config(route_name="events.tickets.boundtickets.edit", renderer='ticketing:templates/tickets/events/tickets/new.html', 
                 request_method="GET")
    @view_config(route_name='tickets.templates.edit', renderer='ticketing:templates/tickets/templates/new.html',
                 request_method="GET")
    def edit(self):
        template = self.context.tickets_query().filter_by(
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

    @view_config(route_name="events.tickets.boundtickets.edit", renderer='ticketing:templates/tickets/events/tickets/new.html', 
                 request_method="POST")
    @view_config(route_name='tickets.templates.edit', renderer='ticketing:templates/tickets/templates/new.html',
                 request_method="POST")
    def edit_post(self):
        template = self.context.tickets_query().filter_by(
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
        return self.context.after_ticket_action_redirect()


    @view_config(route_name='events.tickets.boundtickets.delete', request_method="GET", 
                 renderer="ticketing:templates/tickets/events/_deleteform.html")
    def delete(self):
        ticket_id = self.request.matchdict["id"]
        event_id = self.request.matchdict["event_id"]
        message = u"このチケットテンプレートを削除します。よろしいですか？"
        next_to = self.request.route_path("events.tickets.boundtickets.delete",
                                          id=ticket_id,
                                          event_id=event_id)
        return dict(message=message, next_to=next_to)

    @view_config(route_name='events.tickets.boundtickets.delete', request_method="POST")
    @view_config(route_name='tickets.templates.delete', request_method="POST")
    def delete_post(self):
        template = self.context.tickets_query().filter_by(
            organization_id=self.context.user.organization_id,
            id=self.request.matchdict["id"]).first()

        if template is None:
            raise HTTPNotFound("this is not found")

        template.delete()
        self.request.session.flash(u'チケットテンプレートを削除しました')

        return self.context.after_ticket_action_redirect()

    @view_config(route_name='events.tickets.boundtickets.show', renderer='ticketing:templates/tickets/events/tickets/show.html')
    @view_config(route_name='tickets.templates.show', renderer='ticketing:templates/tickets/templates/show.html')
    def show(self):
        qs = self.context.tickets_query().filter_by(id=self.request.matchdict['id'])
        template = qs.filter_by(organization_id=self.context.user.organization_id).one()
        return dict(h=helpers, template=template)

    @view_config(route_name="events.tickets.boundtickets.download")
    @view_config(route_name='tickets.templates.download')
    def download(self):
        qs = self.context.tickets_query().filter_by(id=self.request.matchdict['id'])
        template = qs.filter_by(organization_id=self.context.user.organization_id).one()
        return FileLikeResponse(StringIO(template.drawing),
                                request=self.request)

    @view_config(route_name="events.tickets.boundtickets.data", renderer="json")
    @view_config(route_name='tickets.templates.data', renderer='json')
    def data(self):
        qs = self.context.tickets_query().filter_by(id=self.request.matchdict['id'])
        template = qs.filter_by(organization_id=self.context.user.organization_id).one()
        data = dict(template.ticket_format.data)
        data.update(dict(drawing=' '.join(to_opcodes(etree.ElementTree(etree.fromstring(template.drawing))))))
        return data

@view_defaults(decorator=with_bootstrap, permission="event_editor")
class TicketPrinter(BaseView):

    @view_config(route_name='tickets.printer', renderer='ticketing:templates/tickets/printer.html')
    def printer(self):
        return dict()

    @view_config(route_name='tickets.print.dequeue', renderer='json')
    def dequeue(self):

        from ticketing.tickets.utils import SvgPageSet
        from datetime import datetime

        queues = TicketPrintQueue.dequeue_all(self.context.user)
        tickets = []
        now = datetime.now()

        svg_page_set = SvgPageSet()
        for queue in queues:
            #queue.deleted_at = now
            tickets.append(dict(
                id = queue.id,
            ))

            data = queue.data['drawing']
            svg_page_set.append_page(data)

        return dict(
            svg = svg_page_set.merge(),
            tickets = tickets
        )

