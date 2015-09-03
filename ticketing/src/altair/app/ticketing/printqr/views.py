# -*- coding:utf-8 -*-

import re
import json
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPForbidden, HTTPNotFound
from datetime import datetime
import logging
import traceback

from altair.app.ticketing.qr import get_qrdata_builder
from altair.app.ticketing.qr.builder import InvalidSignedString

from altair.app.ticketing.models import DBSession
from altair.app.ticketing.core.models import Event
from altair.app.ticketing.core.models import Performance
from altair.app.ticketing.core.models import PageFormat
from altair.app.ticketing.core.models import Ticket
from altair.app.ticketing.core.utils import PrintedAtBubblingSetter
from altair.app.ticketing.orders.models import OrderedProductItemToken

from altair.app.ticketing.qr.utils import get_matched_token_query_from_order_no
from altair.app.ticketing.qr.utils import get_or_create_matched_history_from_token
from altair.app.ticketing.qr.utils import make_data_for_qr
from altair.app.ticketing.payments.plugins import ORION_DELIVERY_PLUGIN_ID
import altair.app.ticketing.orders.orion as orion_api
from altair.app.ticketing.orderreview.api import send_to_orion
from altair.app.ticketing.qr.utils import build_qr_by_orion

from . import forms
from . import helpers as h
from . import utils
from . import todict

logger = logging.getLogger(__name__)

def _accepted_object(request, obj):
    if obj is None:
        raise HTTPNotFound
    if request.context.organization is None:
        request.session.flash(u"ログインしていません")
        raise HTTPForbidden        
    if unicode(obj.organization_id) != unicode(request.context.organization.id):
        logger.info(str((unicode(obj.organization_id) , unicode(request.context.organization.id))))
        request.session.flash(u"ログインしたアカウントとは異なるorganizationです")
        raise HTTPForbidden
    return obj

## misc
@view_config(permission="sales_counter", route_name="misc.order.qr", 
             request_method="GET", 
             renderer="altair.app.ticketing.printqr:templates/misc/orderqr.input.html")
def orderno_input(context, request):
    form = forms.MiscOrderFindForm()
    return {"form": form}

@view_config(permission="sales_counter", route_name="misc.order.qr", 
             request_method="POST", 
             renderer="altair.app.ticketing.printqr:templates/misc/orderqr.input.html")
def orderno_show_qrsigned(context, request):
    form = forms.MiscOrderFindForm(request.POST)
    organization_id = context.operator.organization_id
    if not form.validate() or not form.object_validate(organization_id):
        return {"form": form}
    
    try:
        return orderno_show_qrsigned_after_validated(context, request, form)
    except Exception, e:
        logger.exception(str(e))
        raise

def _signed_string_from_history(builder, history):
    params, ticket = make_data_for_qr(history)
    return builder.sign(builder.make(params))

def orderno_show_qrsigned_after_validated(context, request, form):
    order = _accepted_object(request, form.order)
    request.override_renderer = "altair.app.ticketing.printqr:templates/misc/orderqr.show.html"
    order_no = order.order_no

    tokens = get_matched_token_query_from_order_no(order_no)

    if (order.performance.orion is not None
        and order.performance.orion.qr_enabled
        and order.payment_delivery_pair.delivery_method.delivery_plugin_id == ORION_DELIVERY_PLUGIN_ID):
        histories = []
        for token in tokens:
            response = send_to_orion(request, context, None, token)
            if response['result'] == u"OK" and response.has_key('serial'):
                fake_history = type('FakeTicketPrintHistory', (), {
                    'id': response['serial'],
                    'performance': order.performance,
                    'order': order,
                    'ordered_product_item': token.item,
                    'item_token': token,
                    'seat': token.seat,
                })
                qr = build_qr_by_orion(request, fake_history, response['serial'])
                histories.append(qr)
    else:
        histories = (get_or_create_matched_history_from_token(order_no, tk) for tk in tokens)

    builder = get_qrdata_builder(request)

    signed_history_doubles = sorted([(_signed_string_from_history(builder, history), history) for history in histories], key=lambda xs : xs[1].id)
    return {"signed_history_doubles": signed_history_doubles, "order": order}


## progress notify
@view_config(permission="sales_counter", route_name="progress", 
             renderer="altair.app.ticketing.printqr:templates/progress.html")
def progress_notify_view(context, request):
    event_id = request.matchdict["event_id"]
    event = Event.query.filter_by(id=event_id).first()
    event = _accepted_object(request, event)
    form = forms.PerformanceSelectForm(event_id=event_id)
    return dict(json=json, 
                form=form, 
                endpoints=context.applet_endpoints, 
                api_resource=context.api_resource)
    
@view_config(permission="sales_counter", route_name="api.progress.total_result_data", 
             renderer="json", request_method="GET")
def progress_total_result_data(context, request):
    performance_id = request.GET["performance_id"]
    event_id = request.matchdict["event_id"]

    return dict(
        status="success", 
        data=dict(
            performance=utils.performance_data_from_performance_id(event_id, performance_id), 
            total_result=utils.total_result_data_from_performance_id(event_id, performance_id), 
            current_time=h.japanese_datetime(datetime.now())))
## event list

@view_config(permission="sales_counter", route_name="eventlist", 
             renderer="altair.app.ticketing.printqr:templates/eventlist.html")
def choice_event_view(context, request):
    now = datetime.now()
    events = Event.query.filter_by(organization_id=context.operator.organization_id)
    events = events.filter(Performance.event_id==Event.id)
    events = events.distinct(Event.id)
    return dict(events=events, now=now)

## app

@view_config(permission="sales_counter", route_name="qrapp", 
             renderer="altair.app.ticketing.printqr:templates/qrapp.html")
def qrapp_view(context, request):
    event_id = request.matchdict["event_id"]
    event = Event.query.filter_by(id=event_id).first()
    event = _accepted_object(request, event)
    return dict(json=json, 
                event=event, 
                form = forms.PerformanceSelectForm(event_id=event_id), 
                endpoints=context.applet_endpoints, 
                api_resource=context.api_resource)

@view_config(route_name="api.ticket.data", renderer="json", 
             request_param="qrsigned", xhr=True)
def ticketdata_from_qrsigned_string(context, request):
    builder = get_qrdata_builder(request)
    event_id = request.matchdict.get("event_id", "*")
    signed = request.params["qrsigned"]
    signed = re.sub(r"[\x01-\x1F\x7F]", "", signed.encode("utf-8")).replace("\x00", "") .decode("utf-8")

    try:
        logger.info("signed = %s" % signed)
        qrdata = builder.data_from_signed(signed)
        logger.info("decoded = %s" % qrdata)
        
        if not (qrdata.has_key("order") and qrdata.has_key("serial") and qrdata.has_key("performance")):
            raise Exception("Broken QR: %s" % qrdata)
        
        performance = Performance.query.filter_by(code=qrdata["performance"]).first()
        if performance is None:
            raise Exception("No such performance: %s" % qrdata["performance"])

        order = data = None
        if performance.orion is not None and performance.orion.qr_enabled == 1:
            # coupon_2_qr_enabledは判定には使わない

            res = orion_api.search(request, dict(serial = qrdata["serial"]))

            if res is None:
                raise Exception("Cannot open http connection to Orion API")
            if not res.has_key("result"):
                raise Exception("Unexpected response from Orion")
            if res["result"] != "OK":
                if res.get("errcode") != 'E008': # "No such ticket with serial
                    raise Exception("Orion API failed: %s" % res_text)
            else:
                if not res.has_key("token"):
                    raise Exception("Unexpected response from Orion: %s" % res_text)
                order_and_token = utils.order_from_token(res["token"], qrdata["order"])
                if order_and_token is None:
                    raise Exception("No such ticket: token=%s, order=%s" % (res["token"], qrdata["order"]))
                order, token = order_and_token
                data = todict.data_dict_from_order(order, token)

        if order is None:
            # legacy QR
            order_and_history = utils.order_and_history_from_qrdata(qrdata)
            if order_and_history is None:
                raise Exception("No such ticket: %s" % qrdata)
            order, history = order_and_history
            data = todict.data_dict_from_order_and_history(order, history)

        utils.verify_order(order, event_id=event_id)
        return {"status": "success", 
                "data": data}
    except InvalidSignedString:
        return {"status": "error", "message": u"不正なQRコードです"}
    except KeyError, e:
        logger.info(traceback.format_exc())
        return {"status": "error", "message": u"うまくQRコードを読み込むことができませんでした"}
    except utils.UnmatchEventException:
        return {"status": "error", "message": u"異なるイベントのQRチケットです。このページでは発券できません"}
    except Exception as e:
        logger.warn("%s: %s" % (e.__class__.__name__,  str(e)))
        logger.exception(str(e))
        return {"status": "error", "message": str(e)}

@view_config(route_name="api.ticket.refresh.printed_status", renderer="json", xhr=True)
def refresh_printed_status(context, request):
    token_id = request.json_body["ordered_product_item_token_id"]
    order_no = request.json_body["order_no"]

    token = get_matched_token_query_from_order_no(order_no).filter(OrderedProductItemToken.id==token_id).first()
    token.refreshed_at = datetime.now()
    logger.info("*api.refresh.printed: force refresh status `printed_at' (token_id={0}, printed_at={1}, refreshed_at={2})".format(
            token.id, token.printed_at, token.refreshed_at
            ))
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
    
    if token.is_printed() and not force_update:
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
    logger.info("*qrlog* print ticket token=%s, printed_at=%s" % (token_id, token.printed_at))
    return {"status": "success", "data": {"printed": str(now_time)}}

@view_config(route_name="api.ticket.after_printed_order", renderer="json", xhr=True)
def ticket_after_printed_edit_status_order(context, request):
    token_id = request.json_body["ordered_product_item_token_id"]
    order_no = request.json_body["order_no"]
    order_id = request.json_body["order_id"]
    consumed_tokens = request.json_body["consumed_tokens"]

    tokens = get_matched_token_query_from_order_no(order_no)
    now_time = datetime.now()
    setter = PrintedAtBubblingSetter(now_time)

    for token in tokens:
        if token.id in consumed_tokens:
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
                u'ticket_formats': [todict.ticket_format_to_dict(ticket_format) for ticket_format in dict((ticket.ticket_format.id, ticket.ticket_format) for ticket in tickets).itervalues()],
                u'page_formats':  [
                    todict.page_format_to_dict(page_format) \
                    for page_format in DBSession.query(PageFormat).filter_by(organization=self.context.organization)
                ], 
                u'ticket_templates': [todict.ticket_to_dict(ticket) for ticket in tickets]
                }
            }
        return params

    @view_config(route_name='api.applet.ticket_data', request_method='POST', renderer='json')
    def ticket_data(self): ## svg one
        ordered_product_item_token_id = self.request.json_body.get('ordered_product_item_token_id')
        if ordered_product_item_token_id is None:
            logger.error("no ordered_product_item_token_id given: token id=%s,  organization id=%s" \
                             % (ordered_product_item_token_id, self.context.organization.id))
            return { u'status': u'error', u'message': u'券面取得用の番号がみつかりません' }

        ordered_product_item_token = utils.get_matched_ordered_product_item_token(
            ordered_product_item_token_id, 
            self.context.organization.id)

        if ordered_product_item_token is None:
            logger.error("no ordered_product_item_token found: token id=%s,  organization id=%s" \
                             % (ordered_product_item_token_id, self.context.organization.id))
            return { u'status': u'error', u'message': u'券面データがみつかりません' }

        ticket_templates = utils.enable_ticket_template_list(ordered_product_item_token)
        issuer = utils.get_issuer()
        vardict = todict.svg_data_from_token(ordered_product_item_token, issuer=issuer)
        retval = todict.svg_data_list_all_template_valiation(vardict, ticket_templates)
        if not retval:
            logger.error("no applicable tickets found: token id=%s,  organization id=%s" \
                             % (ordered_product_item_token_id, self.context.organization.id))
            return { u'status': u'error', u'message': u'印刷対象となる券面データがありません' }
        return {
            u'status': u'success',
            u'data': retval
            }

    @view_config(route_name='api.applet.ticket_data_order', request_method='POST', renderer='json')
    def ticket_data_order(self):
        order_no = self.request.json_body.get('order_no')
        if order_no is None:
            return { u'status': u'error', u'message': u'注文番号がみつかりません' }

        tokens = get_matched_token_query_from_order_no(order_no).all()
        retval = []
        templates_generator = utils.EnableTicketTemplatesCache()
        issuer = utils.get_issuer()
        try:
            for ordered_product_item_token in tokens:
                history = get_or_create_matched_history_from_token(order_no, ordered_product_item_token)
                ticket_templates = templates_generator(ordered_product_item_token)

                vardict = todict.svg_data_from_token(ordered_product_item_token, issuer=issuer)
                vardict[u'codeno'] = history.id #一覧で選択するため

                retval.extend(todict.svg_data_list_all_template_valiation(vardict, ticket_templates))
            return {
                u'status': u'success',
                u'data': retval
                }
        except Exception, e:
            logger.error(str(e))
            return { u'status': u'error', u'message': u'不正な注文番号のようです' }

    @view_config(route_name='api.applet.history', request_method='POST', renderer='json') #deprecated
    def history(self):
        history = utils.add_history(
            self.request, 
            self.context.operator.id,
            self.request.json_body
            )
        DBSession.add(history)
        return { u'status': u'success' }
