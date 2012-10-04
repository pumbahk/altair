# -*- coding: utf-8 -*-
import logging
from StringIO import StringIO
import json
import webhelpers.paginate as paginate
import sqlalchemy as sa
from sqlalchemy.orm.exc import NoResultFound
from datetime import datetime
from lxml import etree
from ticketing.fanstatic import with_bootstrap
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound

from ..utils import json_safe_coerce
from ..views import BaseView
from ..models import DBSession
from ..core.models import DeliveryMethod
from ..core.models import TicketFormat, PageFormat, Ticket
from ..core.models import TicketPrintQueueEntry, TicketPrintHistory
from ..core.models import OrderedProductItemToken, OrderedProductItem, OrderedProduct, Order
from . import forms
from . import helpers
from .utils import SvgPageSetBuilder, build_dict_from_ordered_product_item_token, _default_builder
from .response import FileLikeResponse
from .convert import to_opcodes

def ticket_format_to_dict(ticket_format):
    data = dict(ticket_format.data)
    data[u'id'] = ticket_format.id
    data[u'name'] = ticket_format.name
    return data

def ticket_to_dict(ticket):
    data = dict(ticket.data)
    data[u'id'] = ticket.id
    data[u'name'] = ticket.name
    data[u'ticket_format_id'] = ticket.ticket_format_id
    return data

def page_format_to_dict(page_format):
    data = dict(page_format.data)
    data[u'id'] = page_format.id
    data[u'name'] = page_format.name
    data[u'printer_name'] = page_format.printer_name
    return data

def page_formats_for_organization(organization):
    return [
        page_format_to_dict(page_format) \
        for page_format in DBSession.query(PageFormat).filter_by(organization=organization)
        ]

@view_defaults(decorator=with_bootstrap, permission="event_editor")
class TicketMasters(BaseView):
    @view_config(route_name='tickets.index', renderer='ticketing:templates/tickets/index.html', request_method="GET")
    def index(self):
        ticket_format_sort_by, ticket_format_direction = helpers.sortparams('ticket_format', self.request, ('updated_at', 'desc'))

        page_format_sort_by, page_format_direction = helpers.sortparams('page_format', self.request, ('updated_at', 'desc'))

        ticket_template_sort_by, ticket_template_direction = helpers.sortparams('ticket_template', self.request, ('updated_at', 'desc'))

        ticket_format_qs = TicketFormat.filter_by(organization_id=self.context.user.organization_id)
        page_format_qs = PageFormat.filter_by(organization_id=self.context.user.organization_id)
        ticket_template_qs = Ticket.templates_query().filter_by(organization_id=self.context.user.organization_id)

        ticket_format_qs = ticket_format_qs.order_by(helpers.get_direction(ticket_format_direction)(ticket_format_sort_by))

        ticket_template_qs = ticket_template_qs.order_by(helpers.get_direction(ticket_template_direction)(ticket_template_sort_by))
        return dict(h=helpers, page_formats=page_format_qs, ticket_formats=ticket_format_qs, templates=ticket_template_qs)

@view_defaults(decorator=with_bootstrap, permission="event_editor")
class TicketFormats(BaseView):
    @view_config(route_name="tickets.ticketformats.edit",renderer='ticketing:templates/tickets/ticketformats/new.html')
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
        
    @view_config(route_name='tickets.ticketformats.edit', renderer='ticketing:templates/tickets/ticketformats/new.html', request_method="POST")
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

    @view_config(route_name='tickets.ticketformats.new', renderer='ticketing:templates/tickets/ticketformats/new.html')
    def new(self):
        ## ugly
        form = forms.TicketFormatForm(organization_id=self.context.user.organization_id, 
                                      data_value=u"""\
{
  "size": {"width": "", "height": ""},
  "perforations": {"vertical": [], "horizontal": []}, 
  "printable_areas": [{"x": "", "y": "", "width": "", "height":""}],
  "print_offset": {"x": "", "y": ""}
}
""")
        return dict(h=helpers, form=form)

    @view_config(route_name='tickets.ticketformats.new', renderer='ticketing:templates/tickets/ticketformats/new.html', 
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

    @view_config(route_name='tickets.ticketformats.new', renderer='ticketing:templates/tickets/ticketformats/new.html', request_method="POST")
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
            

    @view_config(route_name='tickets.ticketformats.delete', request_method="POST")
    def delete_post(self):
        format = TicketFormat.filter_by(organization_id=self.context.user.organization_id,
                                    id=self.request.matchdict["id"]).first()
        if format is None:
            raise HTTPNotFound("this is not found")

        format.delete()
        self.request.session.flash(u'チケット様式を削除しました')

        return HTTPFound(location=self.request.route_path("tickets.index"))

    @view_config(route_name='tickets.ticketformats.show', renderer='ticketing:templates/tickets/ticketformats/show.html')
    def show(self):
        qs = TicketFormat.filter_by(id=self.request.matchdict['id'])
        format = qs.filter_by(organization_id=self.context.user.organization_id).one()
        return dict(h=helpers, format=format)

    @view_config(route_name='tickets.ticketformats.data', renderer='json')
    def data(self):
        qs = TicketFormat.filter_by(id=self.request.matchdict['id'])
        format = qs.filter_by(organization_id=self.context.user.organization_id).one()
        return format.data

@view_defaults(decorator=with_bootstrap, permission="event_editor")
class PageFormats(BaseView):
    @view_config(route_name="tickets.pageformats.edit",renderer='ticketing:templates/tickets/pageformats/new.html')
    def edit(self):
        format = PageFormat.filter_by(organization_id=self.context.user.organization_id,
                                    id=self.request.matchdict["id"]).first()
        if format is None:
            raise HTTPNotFound("this is not found")

        form = forms.PageFormatForm(organization_id=self.context.user.organization_id, 
                                      name=format.name, 
                                      printer_name=format.printer_name,
                                      data_value=json.dumps(format.data))
        return dict(h=helpers, form=form, format=format)
        
    @view_config(route_name='tickets.pageformats.edit', renderer='ticketing:templates/tickets/pageformats/new.html', request_method="POST")
    def edit_post(self):
        format = PageFormat.filter_by(organization_id=self.context.user.organization_id,
                                    id=self.request.matchdict["id"]).first()
        if format is None:
            raise HTTPNotFound("this is not found")

        form = forms.PageFormatForm(organization_id=self.context.user.organization_id, 
                                      formdata=self.request.POST)
        if not form.validate():
            return dict(h=helpers, form=form, format=format)
        
        params = form.data
        format.name = params["name"]
        format.printer_name = params["printer_name"]
        format.data = params["data_value"]
        format.save()
        self.request.session.flash(u'チケット様式を更新しました')
        return HTTPFound(location=self.request.route_path("tickets.index"))

    @view_config(route_name='tickets.pageformats.new', renderer='ticketing:templates/tickets/pageformats/new.html')
    def new(self):
        ## ugly
        form = forms.PageFormatForm(organization_id=self.context.user.organization_id, 
                                      data_value=u"""\
{
  "size": { "width": "", "height": "" },
  "orientation": "",
  "paper": null,
  "perforations": {
    "vertical": [],
    "horizontal": []
  },
  "printable_area": { "x": "", "y": "", "width": "", "height": "" },
  "ticket_margin": { "left": "", "top": "", "right": "", "bottom": "" }
}
""")
        return dict(h=helpers, form=form)

    @view_config(route_name='tickets.pageformats.new', renderer='ticketing:templates/tickets/pageformats/new.html', 
                 request_param="id")
    def new_with_baseobject(self):
        format = PageFormat.filter_by(organization_id=self.context.user.organization_id,
                                    id=self.request.params["id"]).first()
        if format is None:
            raise HTTPNotFound("this is not found")

        form = forms.PageFormatForm(organization_id=self.context.user.organization_id, 
                                      name=format.name, 
                                      data_value=json.dumps(format.data), 
                                      delivery_methods=[m.id for m in format.delivery_methods])
        return dict(h=helpers, form=form)

    @view_config(route_name='tickets.pageformats.new', renderer='ticketing:templates/tickets/pageformats/new.html', request_method="POST")
    def new_post(self):
        form = forms.PageFormatForm(organization_id=self.context.user.organization_id, 
                                      formdata=self.request.POST)
        if not form.validate():
            return dict(h=helpers, form=form)
        
        params = form.data
        ticket_format = PageFormat(name=params["name"], 
                                printer_name=params["printer_name"],
                                data=params["data_value"],
                                organization_id=self.context.user.organization_id
                                )

        ticket_format.save()
        self.request.session.flash(u'チケット様式を登録しました')
        return HTTPFound(location=self.request.route_path("tickets.index"))
            

    @view_config(route_name='tickets.pageformats.delete', request_method="POST")
    def delete_post(self):
        format = PageFormat.filter_by(organization_id=self.context.user.organization_id,
                                    id=self.request.matchdict["id"]).first()
        if format is None:
            raise HTTPNotFound("this is not found")

        format.delete()
        self.request.session.flash(u'チケット様式を削除しました')

        return HTTPFound(location=self.request.route_path("tickets.index"))

    @view_config(route_name='tickets.pageformats.show', renderer='ticketing:templates/tickets/pageformats/show.html')
    def show(self):
        qs = PageFormat.filter_by(id=self.request.matchdict['id'])
        format = qs.filter_by(organization_id=self.context.user.organization_id).one()
        return dict(h=helpers, format=format)

    @view_config(route_name='tickets.pageformats.data', renderer='json')
    def data(self):
        qs = PageFormat.filter_by(id=self.request.matchdict['id'])
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
class TicketPrintQueueEntries(BaseView):
    @view_config(route_name='tickets.queue.index', renderer='ticketing:templates/tickets/queue/index.html')
    def index(self):
        queue_entries_sort_by, queue_entries_direction = helpers.sortparams('queue_entry', self.request, ('TicketPrintQueueEntry.created_at', 'desc'))
        queue_entries_qs = DBSession.query(TicketPrintQueueEntry) \
            .filter_by(operator=self.context.user, processed_at=None) \
            .join(OrderedProductItem.ordered_product) \
            .join(OrderedProduct.order)
        queue_entries_qs = queue_entries_qs.order_by(helpers.get_direction(queue_entries_direction)(queue_entries_sort_by))
        return dict(h=helpers, queue_entries=queue_entries_qs)

    @view_config(route_name='tickets.queue.delete', request_method="POST")
    def delete(self):
        ids = self.request.params.getall('id')
        n = DBSession.query(TicketPrintQueueEntry) \
            .filter_by(operator=self.context.user) \
            .filter(TicketPrintQueueEntry.id.in_(ids)) \
            .delete(synchronize_session=False)
        self.request.session.flash(u'エントリを %d 件削除しました' % n)
        return HTTPFound(location=self.request.route_path("tickets.queue.index"))

@view_defaults(decorator=with_bootstrap, permission="event_editor")
class TicketPrinter(BaseView):
    @property
    def endpoints(self):
        return dict(
            (key, self.request.route_path('tickets.printer.api.%s' % key))
            for key in ['formats', 'peek', 'dequeue']
            )

    @view_config(route_name='tickets.printer', renderer='ticketing:templates/tickets/printer.html')
    def printer(self):
        return dict(endpoints=self.endpoints)

    @view_config(route_name='tickets.printer', renderer='ticketing:templates/tickets/printer.embedded.html', custom_predicates=(lambda c, r: '__embedded__' in r.GET,))
    def printer_embedded(self):
        return dict(
            endpoints=self.endpoints,
            orders=DBSession.query(Order) \
                   .join(OrderedProduct) \
                   .join(OrderedProductItem) \
                   .join(TicketPrintQueueEntry) \
                   .filter_by(operator=self.context.user))

    @view_config(route_name='tickets.printer.api.enqueue', request_method='POST', renderer='json')
    def enqueue(self):
        ticket_format_id = self.request.json_body['ticket_format_id']
        TicketPrintQueueEntry.enqueue(self.context.user)

    @view_config(route_name='tickets.printer.api.formats', renderer='json')
    def formats(self):
        ticket_formats = []
        for ticket_format in DBSession.query(TicketFormat).filter_by(organization=self.context.organization):
            ticket_formats.append(ticket_format_to_dict(ticket_format))
        return { u'status': u'success',
                 u'data': { u'page_formats': page_formats_for_organization(self.context.organization),
                            u'ticket_formats': ticket_formats } }

    @view_config(route_name='tickets.printer.api.ticket', renderer='json')
    def ticket(self):
        event_id = self.request.matchdict['event_id']
        ticket_id = self.request.matchdict['id'].strip()
        q = DBSession.query(Ticket) \
            .filter_by(organization_id=self.context.organization.id)
        if event_id != '*':
            q = q.filter_by(event_id=event_id)
        if ticket_id:
            q = q.filter_by(id=ticket_id)
        tickets = q.all()
        return {
            u'status': 'success',
            u'data': {
                u'ticket_formats': [ticket_format_to_dict(ticket_format) for ticket_format in dict((ticket.ticket_format.id, ticket.ticket_format) for ticket in tickets).itervalues()],
                u'page_formats': page_formats_for_organization(self.context.organization),
                u'ticket_templates': [ticket_to_dict(ticket) for ticket in tickets]
                }
            }

    @view_config(route_name='tickets.printer.api.ticket_data', request_method='POST', renderer='json')
    def ticket_data(self):
        ordered_product_item_token_id = self.request.json_body.get('ordered_product_item_token_id')
        ordered_product_item_id = self.request.json_body.get('ordered_product_item_id')
        try:
            if ordered_product_item_token_id is not None:
                ordered_product_item_token = \
                    DBSession.query(OrderedProductItemToken) \
                    .filter_by(id=ordered_product_item_token_id) \
                    .join(OrderedProductItem) \
                    .join(OrderedProduct) \
                    .join(Order) \
                    .filter_by(organization_id=self.context.organization.id) \
                    .one()
                pair = build_dict_from_ordered_product_item_token(ordered_product_item_token)
                retval = [] 
                if pair is not None:
                    retval.append({
                        u'ordered_product_item_token_id': ordered_product_item_token.id,
                        u'ordered_product_item_id': ordered_product_item_token.item.id,
                        u'order_id': ordered_product_item_token.item.ordered_product.order.id,
                        u'seat_id': ordered_product_item_token.seat_id,
                        u'serial': ordered_product_item_token.serial,
                        u'data': json_safe_coerce(pair[1])
                        })
                return {
                    u'status': u'success',
                    u'data': retval
                    }
            elif ordered_product_item_id is not None:
                ordered_product_item = DBSession.query(OrderedProductItem) \
                    .filter_by(id=ordered_product_item_id) \
                    .join(OrderedProduct) \
                    .join(Order) \
                    .filter_by(organization_id=self.context.organization.id) \
                    .one()
                extra = _default_builder.build_basic_dict_from_ordered_product_item(ordered_product_item)
                retval = []
                for ordered_product_item_token in ordered_product_item.tokens:
                    pair = _default_builder._build_dict_from_ordered_product_item_token(extra, ordered_product_item, ordered_product_item_token)
                    if pair is not None:
                        retval.append({
                            u'ordered_product_item_token_id': ordered_product_item_token.id,
                            u'ordered_product_item_id': ordered_product_item_token.item.id,
                            u'order_id': ordered_product_item_token.item.product.order.id,
                            u'seat_id': ordered_product_item_token.seat_id,
                            u'serial': ordered_product_item_token.serial,
                            u'data': pair[1]
                            })
                return {
                    u'status': u'success',
                    u'data': retval
                    }
            return { u'status': u'error', u'message': u'insufficient parameters' }
        except NoResultFound:
            return { u'status': u'error', u'message': u'not found' }

    @view_config(route_name='tickets.printer.api.history', request_method='POST', renderer='json')
    def history(self):
        seat_id = self.request.json_body.get(u'seat_id')
        ordered_product_item_token_id = self.request.json_body.get(u'ordered_product_item_token_id')
        ordered_product_item_id = self.request.json_body.get(u'ordered_product_item_id')
        order_id = self.request.json_body.get(u'order_id')
        ticket_id = self.request.json_body[u'ticket_id']
        DBSession.add(
            TicketPrintHistory(
                operator_id=self.context.user.id,
                seat_id=seat_id,
                item_token_id=ordered_product_item_token_id,
                ordered_product_item_id=ordered_product_item_id,
                order_id=order_id,
                ticket_id=ticket_id
                ))
        return { u'status': u'success' }

    @view_config(route_name='tickets.printer.api.peek', request_method='POST', renderer='lxml')
    def peek(self):
        page_format_id = self.request.json_body['page_format_id']
        ticket_format_id = self.request.json_body['ticket_format_id']
        order_id = self.request.json_body.get('order_id')
        page_format = DBSession.query(PageFormat).filter_by(id=page_format_id).one()
        ticket_format = DBSession.query(TicketFormat).filter_by(id=ticket_format_id).one()
        builder = SvgPageSetBuilder(page_format.data, ticket_format.data)
        tickets_per_page = builder.tickets_per_page
        for entry in TicketPrintQueueEntry.peek(self.context.user, ticket_format_id, order_id=order_id):
            builder.add(etree.fromstring(entry.data['drawing']), entry.id, title=(entry.summary if tickets_per_page == 1 else None))
        return builder.root

    @view_config(route_name='tickets.printer.api.dequeue', request_method='POST', renderer='json')
    def dequeue(self):
        queue_ids = self.request.json_body['queue_ids']
        entries = TicketPrintQueueEntry.dequeue(queue_ids)
        for entry in entries:
            DBSession.add(TicketPrintHistory(
                operator_id=entry.operator_id,
                ordered_product_item_id=entry.ordered_product_item_id,
                seat_id=entry.seat_id,
                ticket_id=entry.ticket_id))

        if entries:
            return { u'status': u'success' }
        else:
            return { u'status': u'error' }


@view_defaults(decorator=with_bootstrap, permission="event_editor")
class QRReaderViewDemo(BaseView):
    @view_config(route_name='tickets.printer', renderer='ticketing:templates/tickets/qrreader-demo.html', custom_predicates=(lambda c, r: '__qrreader_demo__' in r.GET,))
    def qrreader_demo(self):
        return dict(
            endpoints=dict(
                tickettemplates=self.request.route_path('tickets.printer.api.ticket', event_id='*', id=''),
                ticketdata=self.request.route_path('tickets.printer.api.ticket_data'),
                history=self.request.route_path('tickets.printer.api.history')
                ),
            ordered_product_item_tokens= \
                DBSession.query(OrderedProductItemToken) \
                    .join(OrderedProductItem) \
                    .join(OrderedProduct) \
                    .join(Order) \
                    .filter_by(organization_id=self.context.organization.id))

