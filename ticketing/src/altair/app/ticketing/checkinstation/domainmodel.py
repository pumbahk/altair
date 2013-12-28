# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
from altair.app.ticketing.core.models import Performance, Event
import sqlalchemy as sa
import sqlalchemy.orm as orm
from pyramid.decorator import reify

class ChoosablePerformance(object):
    def __init__(self, request, operator):
        self.request = request
        self.operator = operator

    def choosable_performance_query(self, now): #基準日時より前後は後で
        qs = (Performance.query
              .filter(Performance.event_id==Event.id, Event.organization_id==self.operator.organization_id)
              .filter(Performance.id==Performance.id)
              .filter(sa.or_(Performance.end_on>=now, Performance.end_on == None)))
        qs = qs.options(orm.joinedload(Performance.event))
        return qs.distinct(Performance.id).order_by(sa.asc(Performance.start_on))

from altair.app.ticketing.qr import get_qrdata_builder
from altair.app.ticketing.printqr.utils import order_and_history_from_qrdata

class TicketData(object):
    def __init__(self, request, operator):
        self.request = request
        self.operator = operator

    def get_order_and_history_from_signed(self, signed):
        builder = get_qrdata_builder(self.request)
        return order_and_history_from_qrdata(builder.data_from_signed(signed))

from altair.app.ticketing.printqr.utils import get_matched_ordered_product_item_token
from altair.app.ticketing.qr.utils import get_matched_token_query_from_order_no
from altair.app.ticketing.printqr.utils import EnableTicketTemplatesCache

class ItemTokenData(object):
    def __init__(self, request, operator):
        self.request = request
        self.operator = operator

    def get_item_token_from_id(self, token_id):
        organization_id = self.operator.organization_id
        return get_matched_ordered_product_item_token(token_id, organization_id)

    def get_item_token_list_from_order_no(self, order_no):
        return get_matched_token_query_from_order_no(order_no).all()

from altair.app.ticketing.printqr import utils as p_utils
from altair.app.ticketing.printqr import todict as p_todict
from altair.app.ticketing.qr.utils import get_or_create_matched_history_from_token
from altair.app.ticketing.tickets.api import get_svg_builder

class SVGDataSource(object):
    def __init__(self, request):
        self.request = request

    @reify
    def templates_cache(self):
        return EnableTicketTemplatesCache()

    def data_list_for_one(self, token):
        issuer = p_utils.get_issuer()
        svg_builder = get_svg_builder(self.request)

        vardict = p_todict.svg_data_from_token(token, issuer=issuer)
        ticket_templates = self.templates_cache(token)
        vardict["svg_list"] = svg_list_all_template_valiation(svg_builder, vardict.get("data", {}), ticket_templates)
        return [vardict]

    def data_list_for_all(self, order_no, tokens):
        issuer = p_utils.get_issuer()
        svg_builder = get_svg_builder(self.request)

        retval = []
        for ordered_product_item_token in tokens:
            history = get_or_create_matched_history_from_token(order_no, ordered_product_item_token)
            ticket_templates = self.templates_cache(ordered_product_item_token)

            vardict = p_todict.svg_data_from_token(ordered_product_item_token, issuer=issuer)
            vardict[u'codeno'] = history.id #一覧で選択するため
            vardict["svg_list"] = svg_list_all_template_valiation(svg_builder, vardict.get("data", {}), ticket_templates)
            retval.append(vardict)
        return retval

def svg_list_all_template_valiation(svg_builder, vardict, ticket_templates):
    ## var dictは券面のレンダリングに利用する変数のdict
    data_list = []
    for ticket_template in ticket_templates:
        data = {"svg": svg_builder.build(ticket_template, vardict)} 
        data[u'ticket_template_name'] = ticket_template.name
        data[u'ticket_template_id'] = ticket_template.id
        data_list.append(data)
    return data_list
