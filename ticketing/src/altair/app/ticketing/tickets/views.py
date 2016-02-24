# -*- coding: utf-8 -*-
import logging
import sys
from StringIO import StringIO
import json
import webhelpers.paginate as paginate
import sqlalchemy as sa
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import expression as sql_expr
from datetime import datetime
from lxml import etree
from altair.app.ticketing.fanstatic import with_bootstrap
from altair.response import FileLikeResponse
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound

from ..utils import json_safe_coerce
from ..views import BaseView
from altair.app.ticketing.models import DBSession
from altair.app.ticketing.core.models import (
    Event,
    DeliveryMethod,
    TicketFormat,
    PageFormat,
    Ticket,
    TicketCover,
    TicketPrintQueueEntry,
    TicketPrintHistory,
    Seat,
    Product,
    )
from altair.app.ticketing.orders.models import (
    OrderedProductItemToken,
    OrderedProductItem,
    OrderedProduct,
    Order,
    )
from . import forms
from . import helpers
from .utils import SvgPageSetBuilder, FallbackSvgPageSetBuilder, build_dict_from_ordered_product_item_token, _default_builder
from .convert import to_opcodes
from .cleaner import cleanup_svg
from .cleaner.normalize import normalize as normalize_svg
from .cleaner.api import get_xmltree
from altair.app.ticketing.tickets.api import set_visible_ticketformat, set_invisible_ticketformat

logger = logging.getLogger(__name__)

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
        for page_format in DBSession.query(PageFormat).filter_by(organization=organization).order_by(PageFormat.display_order)
        ]

@view_defaults(decorator=with_bootstrap, permission="ticket_editor")
class TicketMasters(BaseView):
    @view_config(route_name='tickets.index', renderer='altair.app.ticketing:templates/tickets/index.html', request_method="GET")
    def index(self):
        ticket_format_sort_by, ticket_format_direction = helpers.sortparams('ticket_format', self.request, ('updated_at', 'desc'))
        page_format_sort_by, page_format_direction = helpers.sortparams('page_format', self.request, ('updated_at', 'desc'))
        ticket_template_sort_by, ticket_template_direction = helpers.sortparams('ticket_template', self.request, ('updated_at', 'desc'))
        ticket_cover_sort_by, ticket_cover_direction = helpers.sortparams('ticket_cover', self.request, ('updated_at', 'desc'))

        ticket_format_qs = TicketFormat.filter_by(organization_id=self.context.user.organization_id)
        from altair.app.ticketing.tickets import VISIBLE_TICKETFORMAT_SESSION_KEY
        if not self.request.session.get(VISIBLE_TICKETFORMAT_SESSION_KEY):
            ticket_format_qs = ticket_format_qs.filter_by(visible=True)
        ticket_format_qs = ticket_format_qs.order_by(TicketFormat.display_order)
        page_format_qs = PageFormat.filter_by(organization_id=self.context.user.organization_id)
        page_format_qs = page_format_qs.order_by(PageFormat.display_order)
        ticket_template_qs = Ticket.templates_query().filter_by(organization_id=self.context.user.organization_id)
        ticket_template_qs = ticket_template_qs.order_by(helpers.get_direction(ticket_template_direction)(ticket_template_sort_by))

        ticket_cover_qs = TicketCover.query.filter_by(organization_id=self.context.user.organization_id)
        ticket_cover_qs = ticket_cover_qs.order_by(helpers.get_direction(ticket_cover_direction)(ticket_cover_sort_by))

        ticket_candidates = [{"name": t.name,"pk": t.id }for t in ticket_template_qs]
        return dict(h=helpers,
                    page_formats=page_format_qs,
                    ticket_formats=ticket_format_qs,
                    templates=ticket_template_qs,
                    covers=ticket_cover_qs,
                    ticket_candidates=json.dumps(ticket_candidates))


@view_defaults(decorator=with_bootstrap, permission="ticket_editor")
class TicketFormats(BaseView):
    @view_config(route_name="tickets.ticketformats.visible")
    def visible(self):
        set_visible_ticketformat(self.request)
        return HTTPFound(self.request.route_path("tickets.index"))

    @view_config(route_name="tickets.ticketformats.invisible")
    def invisible(self):
        set_invisible_ticketformat(self.request)
        return HTTPFound(self.request.route_path("tickets.index"))

    @view_config(route_name="tickets.ticketformats.edit",renderer='altair.app.ticketing:templates/tickets/ticketformats/new.html')
    def edit(self):
        format = TicketFormat.filter_by(organization_id=self.context.user.organization_id,
                                    id=self.request.matchdict["id"]).first()
        if format is None:
            raise HTTPNotFound("this is not found")

        form = forms.TicketFormatForm(organization_id=self.context.user.organization_id,
                                      name=format.name,
                                      data_value=json.dumps(format.data),
                                      delivery_methods=[m.id for m in format.delivery_methods],
                                      display_order=format.display_order,
                                      visible=format.visible)
        return dict(h=helpers, form=form, format=format)

    @view_config(route_name='tickets.ticketformats.edit', renderer='altair.app.ticketing:templates/tickets/ticketformats/new.html', request_method="POST")
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
        format.display_order=params["display_order"]
        format.visible=params["visible"]

        for dmethod in format.delivery_methods:
            format.delivery_methods.remove(dmethod)
        for dmethod in DeliveryMethod.filter(DeliveryMethod.id.in_(form.data["delivery_methods"])):
            format.delivery_methods.append(dmethod)
        format.save()
        self.request.session.flash(u'チケット様式を更新しました')
        return HTTPFound(location=self.request.route_path("tickets.index"))

    @view_config(route_name='tickets.ticketformats.new', renderer='altair.app.ticketing:templates/tickets/ticketformats/new.html')
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

    @view_config(route_name='tickets.ticketformats.new', renderer='altair.app.ticketing:templates/tickets/ticketformats/new.html',
                 request_param="id")
    def new_with_baseobject(self):
        format = TicketFormat.filter_by(organization_id=self.context.user.organization_id,
                                    id=self.request.params["id"]).first()
        if format is None:
            raise HTTPNotFound("this is not found")

        form = forms.TicketFormatForm(organization_id=self.context.user.organization_id,
                                      name=format.name,
                                      data_value=json.dumps(format.data),
                                      delivery_methods=[m.id for m in format.delivery_methods],
                                      visible=format.visible)
        return dict(h=helpers, form=form)

    @view_config(route_name='tickets.ticketformats.new', renderer='altair.app.ticketing:templates/tickets/ticketformats/new.html', request_method="POST")
    def new_post(self):
        form = forms.TicketFormatForm(organization_id=self.context.user.organization_id,
                                      formdata=self.request.POST)
        if not form.validate():
            return dict(h=helpers, form=form)

        params = form.data
        ticket_format = TicketFormat(name=params["name"],
                                data=params["data_value"],
                                organization_id=self.context.user.organization_id,
                                display_order=params["display_order"],
                                visible=params["visible"]
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
        elif len(format.tickets) > 0:
            self.request.session.flash(u'チケットがひもづいているためチケット様式を削除できません')
        else:
            format.delete()
            self.request.session.flash(u'チケット様式を削除しました')
        return HTTPFound(location=self.request.route_path("tickets.index"))

    @view_config(route_name='tickets.ticketformats.show', renderer='altair.app.ticketing:templates/tickets/ticketformats/show.html')
    def show(self):
        qs = TicketFormat.filter_by(id=self.request.matchdict['id'])
        format = qs.filter_by(organization_id=self.context.user.organization_id).first()
        if format is None:
            raise HTTPNotFound("this is not found")

        return dict(h=helpers, format=format)

    @view_config(route_name='tickets.ticketformats.data', renderer='json')
    def data(self):
        qs = TicketFormat.filter_by(id=self.request.matchdict['id'])
        format = qs.filter_by(organization_id=self.context.user.organization_id).first()
        if format is None:
            raise HTTPNotFound("this is not found")

        return format.data

@view_defaults(decorator=with_bootstrap, permission="ticket_editor")
class PageFormats(BaseView):
    @view_config(route_name="tickets.pageformats.edit",renderer='altair.app.ticketing:templates/tickets/pageformats/new.html')
    def edit(self):
        format = PageFormat.filter_by(organization_id=self.context.user.organization_id,
                                    id=self.request.matchdict["id"]).first()
        if format is None:
            raise HTTPNotFound("this is not found")

        form = forms.PageFormatForm(organization_id=self.context.user.organization_id,
                                      name=format.name,
                                      printer_name=format.printer_name,
                                      data_value=json.dumps(format.data),
                                      display_order=format.display_order)
        return dict(h=helpers, form=form, format=format)

    @view_config(route_name='tickets.pageformats.edit', renderer='altair.app.ticketing:templates/tickets/pageformats/new.html', request_method="POST")
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
        format.display_order = params["display_order"]
        format.save()
        self.request.session.flash(u'チケット様式を更新しました')
        return HTTPFound(location=self.request.route_path("tickets.index"))

    @view_config(route_name='tickets.pageformats.new', renderer='altair.app.ticketing:templates/tickets/pageformats/new.html')
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

    @view_config(route_name='tickets.pageformats.new', renderer='altair.app.ticketing:templates/tickets/pageformats/new.html',
                 request_param="id")
    def new_with_baseobject(self):
        format = PageFormat.filter_by(organization_id=self.context.user.organization_id,
                                    id=self.request.params["id"]).first()
        if format is None:
            raise HTTPNotFound("this is not found")

        form = forms.PageFormatForm(organization_id=self.context.user.organization_id,
                                      name=format.name,
                                      data_value=json.dumps(format.data))
        return dict(h=helpers, form=form)

    @view_config(route_name='tickets.pageformats.new', renderer='altair.app.ticketing:templates/tickets/pageformats/new.html', request_method="POST")
    def new_post(self):
        form = forms.PageFormatForm(organization_id=self.context.user.organization_id,
                                      formdata=self.request.POST)
        if not form.validate():
            return dict(h=helpers, form=form)

        params = form.data
        ticket_format = PageFormat(name=params["name"],
                                printer_name=params["printer_name"],
                                data=params["data_value"],
                                display_order=params['display_order'],
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

    @view_config(route_name='tickets.pageformats.show', renderer='altair.app.ticketing:templates/tickets/pageformats/show.html')
    def show(self):
        qs = PageFormat.filter_by(id=self.request.matchdict['id'])
        format = qs.filter_by(organization_id=self.context.user.organization_id).first()
        if format is None:
            raise HTTPNotFound("this is not found")

        return dict(h=helpers, format=format)

    @view_config(route_name='tickets.pageformats.data', renderer='json')
    def data(self):
        qs = PageFormat.filter_by(id=self.request.matchdict['id'])
        format = qs.filter_by(organization_id=self.context.user.organization_id).first()
        if format is None:
            raise HTTPNotFound("this is not found")

        return format.data

@view_defaults(decorator=with_bootstrap, permission="ticket_editor")
class TicketCovers(BaseView):
    @view_config(route_name="tickets.covers.edit",renderer='altair.app.ticketing:templates/tickets/covers/new.html')
    def edit(self):
        cover = TicketCover.filter_by(organization_id=self.context.user.organization_id,
                                    id=self.request.matchdict["id"]).first()
        if cover is None:
            raise HTTPNotFound("this is not found")

        form = forms.TicketCoverForm(organization_id=self.context.user.organization_id,
                                     name=cover.name,
                                     ticket=cover.ticket_id)
        return dict(h=helpers, form=form, cover=cover)

    @view_config(route_name='tickets.covers.edit', renderer='altair.app.ticketing:templates/tickets/covers/new.html', request_method="POST")
    def edit_post(self):
        cover = TicketCover.filter_by(organization_id=self.context.user.organization_id,
                                    id=self.request.matchdict["id"]).first()
        if cover is None:
            raise HTTPNotFound("this is not found")

        form = forms.TicketCoverForm(organization_id=self.context.user.organization_id,
                                      formdata=self.request.POST)
        if not form.validate():
            return dict(h=helpers, form=form, cover=cover)

        params = form.data
        cover.name = params["name"]
        cover.ticket_id = params["ticket"]
        cover.save()
        self.request.session.flash(u'表紙を更新しました')
        return HTTPFound(location=self.request.route_path("tickets.index"))

    @view_config(route_name='tickets.covers.show', renderer='altair.app.ticketing:templates/tickets/covers/show.html')
    def show(self):
        cover = TicketCover.filter_by(organization_id=self.context.user.organization_id,
                                    id=self.request.matchdict["id"]).first()
        if cover is None:
            raise HTTPNotFound("this is not found")
        return dict(h=helpers, cover=cover, event=getattr(self.request.context, 'event', None))

    @view_config(route_name="tickets.covers.new", renderer="altair.app.ticketing:templates/tickets/covers/new.html",
                 request_method="GET")
    def new(self):
        form = forms.TicketCoverForm(organization_id=self.context.user.organization_id)
        return dict(
            h=helpers,
            form=form,
            event=getattr(self.request.context, 'event', None),
            route_path=self.request.path,
            route_name=u'登録',
            )

    @view_config(route_name='tickets.covers.new', renderer='altair.app.ticketing:templates/tickets/covers/new.html', request_method="POST")
    def new_post(self):
        form = forms.TicketCoverForm(organization_id=self.context.user.organization_id,
                                      formdata=self.request.POST)
        if not form.validate():
            return dict(
                h=helpers,
                form=form,
                event=getattr(self.request.context, 'event', None),
                route_path=self.request.path,
                route_name=u'登録',
                )

        ticket_cover = TicketCover(name=form.data["name"],
                                   ticket_id=form.data["ticket"],
                                   organization_id=self.context.user.organization_id
                                   )

        ticket_cover.save()
        self.request.session.flash(u'表紙を登録しました')
        return HTTPFound(location=self.request.route_path("tickets.index"))

    def delete(self):
        cover_id = self.request.matchdict["id"]
        message = u"このチケットテンプレートを削除します。よろしいですか？"
        next_to = self.request.route_path("events.tickets.covers.delete",
                                          id=cover_id)
        return dict(message=message, next_to=next_to)

    @view_config(route_name='tickets.covers.delete', request_method="POST")
    def delete_post(self):
        cover = TicketCover.filter_by(organization_id=self.context.user.organization_id,
                                    id=self.request.matchdict["id"]).first()
        if cover is None:
            raise HTTPNotFound("this is not found")

        cover.delete()
        self.request.session.flash(u'表紙を削除しました')

        return HTTPFound(location=self.request.route_path("tickets.index"))

@view_defaults(decorator=with_bootstrap, permission="ticket_editor")
class TicketTemplates(BaseView):
    @view_config(route_name="tickets.templates.new", renderer="altair.app.ticketing:templates/tickets/templates/new.html",
                 request_method="GET")
    def new(self):
        form = forms.TicketTemplateForm(context=self.context)
        return dict(
            h=helpers,
            form=form,
            event=getattr(self.request.context, 'event', None),
            route_path=self.request.path,
            route_name=u'登録',
            )

    @view_config(route_name='tickets.templates.new', renderer='altair.app.ticketing:templates/tickets/templates/new.html', request_method="POST")
    def new_post(self):
        form = forms.TicketTemplateForm(context=self.context, formdata=self.request.POST)
        if not form.validate():
            return dict(
                h=helpers,
                form=form,
                event=getattr(self.request.context, 'event', None),
                route_path=self.request.path,
                route_name=u'登録',
                )

        ticket_template = Ticket(name=form.data["name"],
                                 ticket_format_id=form.data["ticket_format_id"],
                                 data=form.data_value,
                                 filename=form.drawing.data.filename,
                                 organization_id=self.context.organization.id
                                 )

        ticket_template.save()
        self.request.session.flash(u'チケットテンプレートを登録しました')
        return HTTPFound(location=self.request.route_path("tickets.index"))

    @view_config(route_name='tickets.templates.edit', renderer='altair.app.ticketing:templates/tickets/templates/new.html',
                 request_method="GET")
    def edit(self):
        template = self.context.tickets_query().filter_by(
            organization_id=self.context.organization.id,
            id=self.request.matchdict["id"]).first()

        if template is None:
            raise HTTPNotFound("this is not found")

        form = forms.TicketTemplateEditForm(
            context=self.context,
            obj=template
            )
        return dict(
            h=helpers,
            form=form,
            template=template,
            event=getattr(self.request.context, 'event', None),
            route_name=u'編集',
            route_path=self.request.path
            )

    @view_config(route_name='tickets.templates.edit', renderer='altair.app.ticketing:templates/tickets/templates/new.html',
                 request_method="POST")
    def edit_post(self):
        template = self.context.tickets_query().filter_by(
            organization_id=self.context.organization.id,
            id=self.request.matchdict["id"]).first()

        if template is None:
            raise HTTPNotFound("this is not found")

        form = forms.TicketTemplateEditForm(
            context=self.context,
            obj=template,
            formdata=self.request.POST)
        if not form.validate():
            return dict(
                h=helpers,
                form=form,
                template=template,
                event=getattr(self.request.context, 'event', None),
                route_name=u'編集',
                route_path=self.request.path,
                )

        template.name = form.data["name"]
        template.ticket_format_id = form.data["ticket_format_id"]
        template.always_reissueable = form.data["always_reissueable"]
        template.principal = form.data["principal"]
        template.cover_print = form.data["cover_print"]
        if form.filename:
            template.filename = form.filename
        if form.data_value:
            template.data = form.data_value
        template.save()
        self.request.session.flash(u'チケットテンプレートを更新しました')
        return self.context.after_ticket_action_redirect(template)

    @view_config(route_name='tickets.templates.update_derivatives', renderer='altair.app.ticketing:templates/tickets/templates/update_derivatives.html')
    def update_derivatives(self):
        template = Ticket.query.filter_by(id=self.request.matchdict['id']).first()
        if template is None:
            raise HTTPNotFound("this is not found")

        tickets = Ticket\
          .query\
          .join(Event)\
          .filter(Ticket.original_ticket_id==self.request.matchdict['id'])

        return dict(h=helpers, tickets=tickets, template=template)

    @view_config(route_name='tickets.templates.update_derivatives', renderer='altair.app.ticketing:templates/tickets/templates/update_derivatives.html', request_method='POST')
    def update_derivatives_post(self):
        template = Ticket.query.filter_by(id=self.request.matchdict['id']).first()
        if template is None:
            raise HTTPNotFound("this is not found")

        tickets = Ticket\
          .query\
          .join(Event)\
          .filter(Ticket.original_ticket_id==self.request.matchdict['id'])

        if self.request.POST.get('do_update'):
            for ticket in tickets:
                ticket.data = template.data
        self.request.session.pop_flash()
        return HTTPFound(location=self.request.route_path("tickets.index"))

    def delete(self):
        ticket_id = self.request.matchdict["id"]
        event_id = self.request.matchdict["event_id"]
        message = u"このチケットテンプレートを削除します。よろしいですか？"
        next_to = self.request.route_path("events.tickets.boundtickets.delete",
                                          id=ticket_id,
                                          event_id=event_id)
        return dict(message=message, next_to=next_to)

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

    @view_config(route_name='tickets.templates.show', renderer='altair.app.ticketing:templates/tickets/templates/show.html')
    def show(self):
        qs = self.context.tickets_query().filter_by(id=self.request.matchdict['id'])
        template = qs.filter_by(organization_id=self.context.organization.id).first()
        if template is None:
            raise HTTPNotFound("this is not found")

        return dict(h=helpers, template=template, event=getattr(self.request.context, 'event', None), ticket_format_id=template.ticket_format_id)

    @view_config(route_name='tickets.templates.download')
    def download(self):
        raw = self.request.params.get('raw')
        qs = self.context.tickets_query().filter_by(id=self.request.matchdict['id'])
        template = qs.filter_by(organization_id=self.context.organization.id).first()
        if template is None:
            raise HTTPNotFound("this is not found")
        if raw:
            stream = StringIO(template.drawing.encode("utf-8"))
        else:
            out = StringIO()
            normalize_svg(StringIO(template.drawing.encode("utf-8")), out, encoding="utf-8")
            out.seek(0)
            xmltree = get_xmltree(out)
            cleanup_svg(xmltree)

            stream = StringIO()
            xmltree.write(stream, encoding="utf-8")
            stream.seek(0)

        return FileLikeResponse(stream, request=self.request, filename="download.svg")

    @view_config(route_name='tickets.templates.data', renderer='json')
    def data(self):
        qs = self.context.tickets_query().filter_by(id=self.request.matchdict['id'])
        template = qs.filter_by(organization_id=self.context.organization.id).first()
        if template is None:
            raise HTTPNotFound("this is not found")
        data = dict(template.ticket_format.data)
        data.update(dict(drawing=' '.join(to_opcodes(etree.ElementTree(etree.fromstring(template.drawing))))))
        return data

@view_defaults(decorator=with_bootstrap, permission="sales_counter")
class TicketPrintQueueEntries(BaseView):
    @view_config(route_name='tickets.queue.index', renderer='altair.app.ticketing:templates/tickets/queue/index.html')
    def index(self):
        queue_entries_qs = DBSession.query(TicketPrintQueueEntry) \
            .filter_by(operator=self.context.user, processed_at=None)\
            .options(joinedload(TicketPrintQueueEntry.seat))

        ## defaultは印刷対象のもののみ表示
        status = self.request.GET.get("status")
        if status == "all":
            pass
        elif status == "masked":
            queue_entries_qs = queue_entries_qs.filter(TicketPrintQueueEntry.masked_at!=None)
        else:
            queue_entries_qs = queue_entries_qs.filter(TicketPrintQueueEntry.masked_at==None)

        ## defaultは印刷順序(TicketPrintQueueEntry.peekの順序)と同じ
        if "queue_entry_sort" in self.request.GET:
            queue_entries_sort_by, queue_entries_direction = helpers.sortparams('queue_entry', self.request, ('TicketPrintQueueEntry.created_at', 'desc'))
            if queue_entries_sort_by == "Order.order_no":
                # queue_entries_qs = queue_entries_qs\
                #     .join(OrderedProductItem.ordered_product) \
                #     .join(OrderedProduct.order)
                ## これはsummaryのフォーマットが"注文 <order_no> - <message>"という形式のため。これで十分
                queue_entries_sort_by = "TicketPrintQueueEntry.summary"
            queue_entries_qs = queue_entries_qs.order_by(helpers.get_direction(queue_entries_direction)(queue_entries_sort_by))
        else:
            queue_entries_qs = queue_entries_qs.order_by(*TicketPrintQueueEntry.printing_order_condition())

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

    @view_config(route_name='tickets.queue.mask', request_method="POST")
    def mask(self):
        ids = self.request.params.getall('id')
        now = datetime.now()
        n = DBSession.query(TicketPrintQueueEntry) \
            .filter_by(operator=self.context.user) \
            .filter(TicketPrintQueueEntry.id.in_(ids), TicketPrintQueueEntry.masked_at==None) \
            .update({"masked_at": now}, synchronize_session=False)
        self.request.session.flash(u'エントリを %d 件除外しました' % n)
        return HTTPFound(location=self.request.route_path("tickets.queue.index"))

    @view_config(route_name='tickets.queue.unmask', request_method="POST")
    def unmask(self):
        ids = self.request.params.getall('id')
        n = DBSession.query(TicketPrintQueueEntry) \
            .filter_by(operator=self.context.user) \
            .filter(TicketPrintQueueEntry.id.in_(ids), TicketPrintQueueEntry.masked_at!=None) \
            .update({"masked_at": None}, synchronize_session=False)
        self.request.session.flash(u'エントリを %d 件元に戻しました' % n)
        return HTTPFound(location=self.request.route_path("tickets.queue.index"))

@view_defaults(decorator=with_bootstrap, permission="sales_counter")
class TicketPrinter(BaseView):
    @property
    def endpoints(self):
        return dict(
            (key, self.request.route_path('tickets.printer.api.%s' % key))
            for key in ['formats', 'peek', 'dequeue', 'list', 'unmask', 'mask', 'delete']
            )

    @view_config(route_name='tickets.printer', renderer='altair.app.ticketing:templates/tickets/printer.html')
    def printer(self):
        return dict(endpoints=self.endpoints)

    @view_config(route_name='tickets.printer2', renderer='altair.app.ticketing:templates/tickets/printer2.html')
    def printer2(self):
        return dict(endpoints=self.endpoints)

    @view_config(route_name='tickets.printer3', renderer='altair.app.ticketing:templates/tickets/printer3.html')
    def printer3(self):
        return dict(endpoints=self.endpoints)

    @view_config(route_name='tickets.printer', renderer='altair.app.ticketing:templates/tickets/printer.embedded.html', custom_predicates=(lambda c, r: '__embedded__' in r.GET,))
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
        for ticket_format in DBSession.query(TicketFormat).filter_by(organization=self.context.organization).order_by(TicketFormat.display_order):
            ticket_formats.append(ticket_format_to_dict(ticket_format))
        return {
            u'status': u'success',
            u'data': {
                u'page_formats': page_formats_for_organization(self.context.organization),
                u'ticket_formats': ticket_formats,
                }
            }

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
                u'page_formats': page_formats_for_organization(self.context.organization),
                u'ticket_formats': [ticket_format_to_dict(ticket_format) for ticket_format in dict((ticket.ticket_format.id, ticket.ticket_format) for ticket in tickets).itervalues()],
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
                d = build_dict_from_ordered_product_item_token(ordered_product_item_token)
                retval = []
                if d is not None:
                    retval.append({
                        u'ordered_product_item_token_id': ordered_product_item_token.id,
                        u'ordered_product_item_id': ordered_product_item_token.item.id,
                        u'order_id': ordered_product_item_token.item.ordered_product.order.id,
                        u'seat_id': ordered_product_item_token.seat_id,
                        u'serial': ordered_product_item_token.serial,
                        u'data': json_safe_coerce(d)
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
        queue_ids = self.request.json_body.get('queue_ids')
        page_format = DBSession.query(PageFormat).filter_by(id=page_format_id).one()
        ticket_format = DBSession.query(TicketFormat).filter_by(id=ticket_format_id).one()
        try:
            builder = SvgPageSetBuilder(page_format.data, ticket_format.data)
        except Exception as e:
            logger.info(u'failed to create SvgPageSetBuilder', exc_info=sys.exc_info())
            builder = FallbackSvgPageSetBuilder(page_format.data, ticket_format.data)
        tickets_per_page = builder.tickets_per_page
        for entry in TicketPrintQueueEntry.peek(self.context.user, ticket_format_id=ticket_format_id, order_id=order_id, queue_ids=queue_ids):
            builder.add(etree.fromstring(entry.data['drawing']), entry.id, title=(entry.summary if tickets_per_page == 1 else None))
        return builder.root

    @view_config(route_name='tickets.printer.api.list', request_method='POST', renderer='json')
    def list(self):
        page_format_id = self.request.json_body['page_format_id']
        ticket_format_id = self.request.json_body['ticket_format_id']
        include_masked = self.request.json_body.get('include_masked', False)
        include_unmasked = self.request.json_body.get('include_unmasked', True)
        order_id = self.request.json_body.get('order_id')
        page_format = DBSession.query(PageFormat).filter_by(id=page_format_id).one()
        ticket_format = DBSession.query(TicketFormat).filter_by(id=ticket_format_id).one()
        try:
            builder = SvgPageSetBuilder(page_format.data, ticket_format.data)
        except Exception as e:
            logger.info(u'failed to create SvgPageSetBuilder', exc_info=sys.exc_info())
            builder = FallbackSvgPageSetBuilder(page_format.data, ticket_format.data)
        tickets_per_page = builder.tickets_per_page
        q = TicketPrintQueueEntry.query(
            self.context.user,
            ticket_format_id=ticket_format_id,
            order_id=order_id,
            include_masked=include_masked,
            include_unmasked=include_unmasked) \
            .outerjoin(TicketPrintQueueEntry.ordered_product_item) \
            .outerjoin(OrderedProductItem.ordered_product) \
            .outerjoin(OrderedProduct.order) \
            .outerjoin(OrderedProduct.product) \
            .outerjoin(TicketPrintQueueEntry.seat) \
            .with_entities(
                TicketPrintQueueEntry.id,
                TicketPrintQueueEntry.summary,
                TicketPrintQueueEntry.masked_at,
                Seat.id,
                Seat.name,
                Product.id,
                Product.name,
                Order.order_no)
        entries = []
        index = 0
        serial = 0
        for queue_id, summary, masked_at, \
                seat_id, seat_name, product_id, product_name, order_no in q:
            unmasked = masked_at is None
            entries.append({
                u'index': index,
                u'serial': serial,
                u'page': int(serial / tickets_per_page) if unmasked else None,
                u'masked': not unmasked,
                u'queue_id': queue_id,
                u'summary': summary,
                u'seat_id': seat_id,
                u'seat_name': seat_name,
                u'product_id': product_id,
                u'product_name': product_name,
                u'order_no': order_no
                })
            index += 1
            if unmasked:
                serial += 1
        return {
            u'status': u'success',
            u'data': json_safe_coerce({
                u'tickets_per_page': tickets_per_page,
                u'entries': entries,
                })
            }

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

    @view_config(route_name='tickets.printer.api.mask', request_method='POST', renderer='json')
    def mask(self):
        now = datetime.now() # XXX
        queue_ids = self.request.json_body['queue_ids']
        DBSession.query(TicketPrintQueueEntry) \
            .filter(TicketPrintQueueEntry.operator_id == self.context.user.id) \
            .filter(TicketPrintQueueEntry.id.in_(queue_ids)) \
            .update({'masked_at': now}, synchronize_session=False)
        return self.list()

    @view_config(route_name='tickets.printer.api.unmask', request_method='POST', renderer='json')
    def unmask(self):
        queue_ids = self.request.json_body['queue_ids']
        DBSession.query(TicketPrintQueueEntry) \
            .filter(TicketPrintQueueEntry.operator_id == self.context.user.id) \
            .filter(TicketPrintQueueEntry.id.in_(queue_ids)) \
            .update({'masked_at': None}, synchronize_session=False)
        return self.list()

    @view_config(route_name='tickets.printer.api.delete', request_method='POST', renderer='json')
    def delete(self):
        queue_ids = self.request.json_body['queue_ids']
        DBSession.query(TicketPrintQueueEntry) \
            .filter(TicketPrintQueueEntry.operator_id == self.context.user.id) \
            .filter(TicketPrintQueueEntry.id.in_(queue_ids)) \
            .delete(synchronize_session=False)
        return self.list()

@view_defaults(decorator=with_bootstrap, permission="sales_counter")
class QRReaderViewDemo(BaseView):
    @view_config(route_name='tickets.printer', renderer='altair.app.ticketing:templates/tickets/qrreader-demo.html', custom_predicates=(lambda c, r: '__qrreader_demo__' in r.GET,))
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
