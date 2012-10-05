# -*- coding:utf-8 -*-

import json
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPBadRequest, HTTPFound
from ticketing.qr import get_qrdata_builder
import logging
from ticketing.printqr import utils 
logger = logging.getLogger(__name__)

from . import forms
from . import security
from ticketing.tickets.utils import build_dict_from_ordered_product_item_token
from ticketing.utils import json_safe_coerce
from ticketing.models import DBSession
from ticketing.core.models import Order
from ticketing.core.models import TicketPrintHistory
from ticketing.core.models import OrderedProductItem
from ticketing.core.models import OrderedProduct
from ticketing.core.models import OrderedProductItemToken
from ticketing.core.models import Ticket
from ticketing.core.utils import PrintedAtBubblingSetter
from datetime import datetime

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
        headers = security.login(request, form.data["login_id"], form.data["password"])
        return HTTPFound(location=request.route_url("index"), headers=headers)

@view_config(route_name="logout", request_method="POST")
def logout_view(request):
    headers = security.logout(request)
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
             request_param="qrsigned", xhr=True)
def ticketdata_from_qrsigned_string(context, request):
    signed = request.params["qrsigned"]
    builder = get_qrdata_builder(request)
    try:
        data = utils.ticketdata_from_qrdata(builder.data_from_signed(signed))
        return data
    except KeyError:
        raise HTTPBadRequest
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.warn("%s: %s" % (e.__class__.__name__,  str(e)))
        raise HTTPBadRequest

@view_config(route_name="api.ticket.after_printed", renderer="json", xhr=True)
def ticket_after_printed_edit_status(context, request):
    token_id = request.json_body["ordered_product_item_token_id"]
    order_no = request.json_body["order_no"]
    force_update = request.json_body.get("force_update")

    token = OrderedProductItemToken.query.filter_by(id=token_id)\
        .filter(OrderedProductItemToken.ordered_product_item_id==OrderedProductItem.id)\
        .filter(OrderedProductItem.ordered_product_id == OrderedProduct.id)\
        .filter(OrderedProduct.order_id==Order.id, Order.order_no==order_no).first()

    if token is None:
        mes = "*after ticket print: token is not found. (token_id = %d,  order_no=%s)"
        logger.warn(mes % (token_id, order_no))
        return {"status": "error", "data": {}, "message": "token is not found"}
    
    if token.printed_at and not force_update:
        mes = "*after ticket print: this ticket is already printed (token_id=%s, printed_at=%s)"
        logger.warn(mes % (token.id, token.printed_at))
        return {"status": "error", "data": {}, "message": "token is already printed"}

    setter = PrintedAtBubblingSetter(datetime.now())
    setter.printed_token(token)
    setter.start_bubbling()
    DBSession.add(token)
    return {"status": "success", "data": {}}

class AppletAPIView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        
    @view_config(route_name='api.applet.ticket', renderer='json')
    def ticket(self):
        event_id = self.request.matchdict['event_id']
        ticket_id = self.request.matchdict['id'].strip()
        q = Ticket.templates_query().filter_by(organization_id=self.context.organization.id)
        if event_id != '*':
            q = q.filter_by(event_id=event_id)
        if ticket_id:
            q = q.filter_by(id=ticket_id)
        tickets = q.all()

        params = {
            u'status': 'success',
            u'data': {
                u'ticket_formats': [utils.ticket_format_to_dict(ticket_format) for ticket_format in dict((ticket.ticket_format.id, ticket.ticket_format) for ticket in tickets).itervalues()],
                u'page_formats': utils.page_formats_for_organization(self.context.organization),
                u'ticket_templates': [utils.ticket_to_dict(ticket) for ticket in tickets]
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
            .filter(Order.organization_id==self.context.organization.id)

        ordered_product_item_token = qs.first()
        if ordered_product_item_token is None:
            logger.debug("*api.applet.ticket data: token id=%s,  organization id=%s" \
                             % (ordered_product_item_token_id, self.context.organization.id))
            return { u'status': u'error', u'message': u'券面データがみつかりません' }

        pair = build_dict_from_ordered_product_item_token(ordered_product_item_token)
        retval = [] 
        if pair is not None:
            retval.append({
                u'ordered_product_item_token_id': ordered_product_item_token.id,
                u'ordered_product_item_id': ordered_product_item_token.item.id,
                u'order_id': ordered_product_item_token.item.ordered_product.order.id,
                u'seat_id': ordered_product_item_token.seat_id or "",
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
