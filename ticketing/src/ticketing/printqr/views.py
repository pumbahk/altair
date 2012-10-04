# -*- coding:utf-8 -*-

import json
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPBadRequest, HTTPFound
from ticketing.qr import get_qrdata_builder
import logging
from ticketing.printqr import utils 
logger = logging.getLogger(__name__)

from . import forms
from .security import login, logout
from ticketing.core.models import Order, TicketPrintHistory, OrderedProductItem, OrderedProduct, OrderedProductItemToken
from ticketing.models import DBSession
from ticketing.core.models import TicketPrintQueueEntry, PageFormat, TicketFormat, Ticket
from ticketing.tickets.utils import SvgPageSetBuilder
from lxml import etree

## login

@view_config(route_name="login", request_method="GET", renderer="ticketing.printqr:templates/login.html")
def login_view(request):
    logger.debug("login")
    form = forms.LoginForm()
    return {"form": form}

@view_config(route_name="login", request_method="POST", renderer="ticketing.printqr:templates/login.html")
def login_post_view(request):
    form = forms.LoginForm(request.POST)
    if not form.validate():
        return {"form": form}
    else:
        headers = login(request, form.data["login_id"], form.data["password"])
        return HTTPFound(location=request.route_url("index"), headers=headers)

@view_config(route_name="logout", request_method="POST")
def logout_view(request):
    headers = logout(request)
    request.session.flash(u"ログアウトしました")
    return HTTPFound(location=request.route_url("login"), headers=headers)

## app

@view_config(permission="sales_counter", route_name="index", 
             renderer="ticketing.printqr:templates/index.html")
def index_view(context, request):
    print context.operator
    return dict(json=json, 
                endpoints=context.applet_endpoints, 
                api_resource=context.api_resource)

@view_config(route_name="api.ticket.data", renderer="json", 
             request_param="qrsigned")
def ticket_data(context, request):
    signed = request.params["qrsigned"]
    builder = get_qrdata_builder(request)
    try:
        data = utils.ticketdata_from_qrdata(builder.data_from_signed(signed))
        return data
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.warn("%s: %s" % (e.__class__.__name__,  str(e)))
        raise HTTPBadRequest

class AppletAPIView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request


    @view_config(route_name='api.applet.enqueue', request_method='POST', renderer='json')
    def enqueue(self):
        try:
            print "enqueue!"
            ticket_format_id = self.request.json_body['ticket_format_id']
            TicketPrintQueueEntry.enqueue(self.context.user)
        except:
            print "--------"
            import traceback
            traceback.print_exc()
        

    @view_config(route_name='api.applet.formats', renderer='json')
    def formats(self):
        try:
            print "formats!!!"
            ## 初回にpeekを走らせるのを止めようと思ったけれど、そうコスト高くないし良いや
            return { u'status': u'success',
                     u'data': { u'ticket_formats': [],
                                u'ticket_templates': []} }
            ticket_formats = []
            for ticket_format in DBSession.query(TicketFormat).filter_by(organization=self.context.organization):
                data = dict(ticket_format.data)
                data[u'id'] = ticket_format.id
                data[u'name'] = ticket_format.name
                data[u"size"] = ticket_format.data["size"]
                data[u"printable_areas"] = ticket_format.data["printable_areas"]
                data[u"perforations"] = ticket_format.data["perforations"]
                ticket_formats.append(data)

            ticket_templates = []
            for ticket_template in Ticket.templates_query().filter_by(organization=self.context.organization):
                data = dict(ticket_template.data)
                data[u'id'] = ticket_template.id
                data[u'name'] = ticket_template.name
                data[u'ticket_format_id'] = ticket_template.ticket_format_id
                data[u"drawing"] = ticket_template.data["drawing"]
                ticket_templates.append(data)
            return { u'status': u'success',
                     u'data': { u'ticket_formats': ticket_formats,
                                u'ticket_templates': ticket_templates} }
        except:
            print "--------"
            import traceback
            traceback.print_exc()

    @view_config(route_name='api.applet.peek', request_method='POST', renderer='lxml')
    def peek(self):
        try:
            print "peeek!"
            page_format_id = self.request.json_body['page_format_id']
            ticket_format_id = self.request.json_body['ticket_format_id']
            order_id = self.request.json_body.get('order_id')

            ## order_idが取得できなかった場合何を返せば良いのだろう？
            # if order_id is None:
            #     return None #xxx:
            page_format = DBSession.query(PageFormat).filter_by(id=page_format_id).one()
            ticket_format = DBSession.query(TicketFormat).filter_by(id=ticket_format_id).one()
            builder = SvgPageSetBuilder(page_format.data, ticket_format.data)
            tickets_per_page = builder.tickets_per_page
            for entry in TicketPrintQueueEntry.peek(self.context.user, ticket_format_id, order_id=order_id):
                builder.add(etree.fromstring(entry.data['drawing']), entry.id, title=(entry.summary if tickets_per_page == 1 else None))
            return builder.root
        except:
            print "--------"
            import traceback
            traceback.print_exc()

    @view_config(route_name='api.applet.dequeue', request_method='POST', renderer='json')
    def dequeue(self):
        try:
            print "dequeue!!!"
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
        except:
            print "--------"
            import traceback
            traceback.print_exc()

    @view_config(route_name='api.applet.ticket', renderer='json')
    def ticket(self):
        ticket_id = self.request.matchdict['id'].strip()
        q = DBSession.query(Ticket) \
            .filter_by(organization_id=self.context.organization.id)
        if ticket_id:
            q = q.filter_by(id=ticket_id)
        tickets = q.all()

        params = {
            u'status': 'success',
            u'data': {
                u'ticket_formats': [ticket_format_to_dict(ticket_format) for ticket_format in dict((ticket.ticket_format.id, ticket.ticket_format) for ticket in tickets).itervalues()],
                u'ticket_templates': [ticket_to_dict(ticket) for ticket in tickets]
                }
            }
        return params

    @view_config(route_name='api.applet.ticket_data', request_method='POST', renderer='json')
    def ticket_data(self):
        ordered_product_item_token_id = self.request.json_body.get('ordered_product_item_token_id')
        if ordered_product_item_token_id is None:
            return { u'status': u'error', u'message': u'券面取得用の番号がみつかりません' }

        qs = DBSession.query(OrderedProductItemToken) \
            .filter_by(id=ordered_product_item_token_id) \
            .join(OrderedProductItem) \
            .join(OrderedProduct) \
            .filter(Order.id==OrderedProduct.order_id) \
            .filter(Order.organization_id==self.context.organization.id) \

        ordered_product_item_token = qs.first()
        if ordered_product_item_token is None:
            return { u'status': u'error', u'message': u'券面データがみつかりません' }

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

    @view_config(route_name='api.applet.history', request_method='POST', renderer='json')
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

from sqlalchemy.orm.exc import NoResultFound
from ticketing.tickets.utils import build_dict_from_ordered_product_item_token, _default_builder
from ticketing.utils import json_safe_coerce
