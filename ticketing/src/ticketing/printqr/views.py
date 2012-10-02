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

## login

@view_config(route_name="login", request_method="GET", renderer="ticketing.printqr:templates/login.html")
def login_view(request):
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
        logger.warn("%s: %s" % (e.__class__.__name__,  str(e)))
        raise HTTPBadRequest

from ticketing.models import DBSession
from ticketing.core.models import TicketPrintQueueEntry, PageFormat, TicketFormat, TicketPrintHistory
from ticketing.tickets.utils import SvgPageSetBuilder
from lxml import etree

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
            # return { u'status': u'success',
            #          u'data': { u'page_formats': [],
            #                     u'ticket_formats': []} }
            page_formats = []
            for page_format in DBSession.query(PageFormat).filter_by(organization=self.context.organization):
                data = dict(page_format.data)
                data[u'id'] = page_format.id
                data[u'name'] = page_format.name
                data[u'printer_name'] = page_format.printer_name
                page_formats.append(data)
            ticket_formats = []
            for ticket_format in DBSession.query(TicketFormat).filter_by(organization=self.context.organization):
                data = dict(ticket_format.data)
                data[u'id'] = ticket_format.id
                data[u'name'] = ticket_format.name
                ticket_formats.append(data)
            return { u'status': u'success',
                     u'data': { u'page_formats': page_formats,
                                u'ticket_formats': ticket_formats } }

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

