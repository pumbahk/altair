# -*- coding:utf-8 -*-

import json
import re
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from ticketing.qr import get_qrdata_builder
import logging
from ticketing.printqr import utils 
logger = logging.getLogger(__name__)

from . import forms
from . import security
from ticketing.models import DBSession
from ticketing.core.models import Event
from ticketing.core.models import Order
from ticketing.core.models import TicketPrintHistory
from ticketing.core.models import OrderedProductItem
from ticketing.core.models import OrderedProduct
from ticketing.core.models import OrderedProductItemToken
from ticketing.core.models import Ticket
from ticketing.core.utils import PrintedAtBubblingSetter
from datetime import datetime

from ticketing.qr.utils import get_matched_token_query_from_order_no
from ticketing.qr.utils import get_or_create_matched_history_from_token
from ticketing.qr.utils import make_data_for_qr

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
        return HTTPFound(location=request.route_url("eventlist"), headers=headers)

@view_config(route_name="logout", request_method="POST")
def logout_view(request):
    headers = security.logout(request)
    request.session.flash(u"ログアウトしました")
    return HTTPFound(location=request.route_url("login"), headers=headers)


## misc
@view_config(permission="sales_counter", route_name="misc.order.qr", 
             request_method="GET", 
             renderer="ticketing.printqr:templates/misc/orderqr.input.html")
def orderno_input(context, request):
    form = forms.MiscOrderFindForm()
    return {"form": form}

@view_config(permission="sales_counter", route_name="misc.order.qr", 
             request_method="POST", 
             renderer="ticketing.printqr:templates/misc/orderqr.input.html")
def orderno_show_qrsigned(context, request):
    form = forms.MiscOrderFindForm(request.POST)
    organization_id = context.operator.organization_id
    if not form.validate() or not form.object_validate(organization_id):
        return {"form": form}
    
    ## boo
    try:
        return orderno_show_qrsigned_after_validated(context, request, form)
    except Exception, e:
        import traceback
        traceback.print_exc()
        raise

def _signed_string_from_history(builder, history):
    params = make_data_for_qr(history)
    return builder.sign(builder.make(params))

def orderno_show_qrsigned_after_validated(context, request, form):
    request.override_renderer = "ticketing.printqr:templates/misc/orderqr.show.html"
    order = form.order
    order_no = order.order_no

    tokens = get_matched_token_query_from_order_no(order_no)
    histories = (get_or_create_matched_history_from_token(order_no, tk) for tk in tokens)
    builder = get_qrdata_builder(request)

    signed_history_doubles = sorted([(_signed_string_from_history(builder, h), h) for h in histories], key=lambda xs : xs[1].id)
    return {"signed_history_doubles": signed_history_doubles, "order": order}
    
## event list

@view_config(permission="sales_counter", route_name="eventlist", 
             renderer="ticketing.printqr:templates/eventlist.html")
def choice_event_view(context, request):
    now = datetime.now()
    events = Event.query.filter_by(organization_id=context.operator.organization_id)
    return dict(events=events, now=now)

## app

@view_config(permission="sales_counter", route_name="qrapp", 
             renderer="ticketing.printqr:templates/qrapp.html")
def qrapp_view(context, request):
    return dict(json=json, 
                endpoints=context.applet_endpoints, 
                api_resource=context.api_resource)

@view_config(route_name="api.ticket.data", renderer="json", 
             request_param="qrsigned", xhr=True)
def ticketdata_from_qrsigned_string(context, request):
    signed = request.params["qrsigned"]
    signed = re.sub(r"[\x01-\x1F\x7F]", "", signed.encode("utf-8")) .decode("utf-8")    
    builder = get_qrdata_builder(request)
    event_id = request.matchdict["event_id"]
    try:
        data = utils.ticketdata_from_qrdata(builder.data_from_signed(signed), event_id=event_id)
        return {"status": "success", 
                "data": data}
    except KeyError, e:
        return {"status": "error", "message": u"うまくQRコードを読み込むことができませんでした"}
    except utils.UnmatchEventException:
        return {"status": "error", "message": u"異なるイベントのQRチケットです。このページでは発券できません"}
    except Exception as e:
        logger.warn("%s: %s" % (e.__class__.__name__,  str(e)))
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

@view_config(route_name="api.ticket.refresh.printed_status", renderer="json", xhr=True)
def refresh_printed_status(context, request):
    logger.info("*api.refresh.printed: force refresh status `printed_at'")
    token_id = request.json_body["ordered_product_item_token_id"]
    order_no = request.json_body["order_no"]

    token = get_matched_token_query_from_order_no(order_no).filter(OrderedProductItemToken.id==token_id).first()
    setter = PrintedAtBubblingSetter(None)
    setter.printed_token(token)
    setter.start_refresh_status_bubbling()
    DBSession.add(token)
    return {"status": "success", "data": {}}
    
@view_config(route_name="api.log", renderer="json", 
             request_param="log")
def log_view(context, request):
    try:
        ## todo:loglevel分ける
        logger.info(request.params["log"])
        return {"status": "success"}
    except Exception, e:
        return {"status": "error", "message": str(e)}
    
@view_config(route_name="api.ticket.after_printed", renderer="json", xhr=True)
def ticket_after_printed_edit_status(context, request):
    token_id = request.json_body["ordered_product_item_token_id"]
    order_no = request.json_body["order_no"]
    force_update = request.json_body.get("force_update")

    token = get_matched_token_query_from_order_no(order_no).filter(OrderedProductItemToken.id==token_id).first()

    if token is None:
        mes = "*after ticket print: token is not found. (token_id = %d,  order_no=%s)"
        logger.warn(mes % (token_id, order_no))
        return {"status": "error", "data": {}, "message": "token is not found"}
    
    if token.printed_at and not force_update:
        mes = "*after ticket print: this ticket is already printed (token_id=%s, printed_at=%s)"
        logger.warn(mes % (token.id, token.printed_at))
        return {"status": "error", "data": {}, "message": "token is already printed"}

    history = utils.add_history(
        request, 
        context.operator.id,
        request.json_body
        )
    DBSession.add(history)

    now_time = datetime.now()
    setter = PrintedAtBubblingSetter(now_time)
    setter.printed_token(token)
    setter.start_bubbling()
    DBSession.add(token)

    ## log
    logger.info("*qrlog* print ticket token=%s" % (token_id))
    return {"status": "success", "data": {"printed": str(now_time)}}

@view_config(route_name="api.ticket.after_printed_order", renderer="json", xhr=True)
def ticket_after_printed_edit_status_order(context, request):
    token_id = request.json_body["ordered_product_item_token_id"]
    order_no = request.json_body["order_no"]
    order_id = request.json_body["order_id"]
    force_update = request.json_body.get("force_update")

    tokens = get_matched_token_query_from_order_no(order_no)
    if not force_update:
        tokens = tokens.filter(OrderedProductItemToken.printed_at == None)

    now_time = datetime.now()
    setter = PrintedAtBubblingSetter(now_time)
    for token in tokens:
        DBSession.add(token)
        DBSession.add(utils.history_from_token(request, context.operator.id, order_id, token))
        setter.printed_token(token)

    setter.start_bubbling()
    ## log
    logger.info("*qrlog* print ticket token=%s" % (token_id))
    return {"status": "success", "data": {"printed": str(now_time)}}

class AppletAPIView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        
    @view_config(route_name='api.applet.ticket', renderer='json')
    def ticket(self):
        event_id = self.request.matchdict['event_id']
        ticket_id = self.request.matchdict['id'].strip()
        q = Ticket.query.filter_by(organization_id=self.context.organization.id)
        if event_id != '*':
            q = q.filter_by(event_id=event_id)
        else:
            logger.warn("*api.applet.ticket: event id is '*'")
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
        retval = utils.svg_data_from_token(ordered_product_item_token)
        return {
            u'status': u'success',
            u'data': retval
            }

    @view_config(route_name='api.applet.ticket_data_order', request_method='POST', renderer='json')
    def ticket_data_order(self):
        order_no = self.request.json_body.get('order_no')
        if order_no is None:
            return { u'status': u'error', u'message': u'注文番号がみつかりません' }

        qs = get_matched_token_query_from_order_no(order_no)
        
        retval = []
        for ordered_product_item_token in qs:
            retval.extend(utils.svg_data_from_token_with_descinfo(ordered_product_item_token))
        return {
            u'status': u'success',
            u'data': retval
            }

    @view_config(route_name='api.applet.history', request_method='POST', renderer='json')
    def history(self):
        history = utils.add_history(
            self.request, 
            self.context.operator.id,
            self.request.json_body
            )
        DBSession.add(history)
        return { u'status': u'success' }
