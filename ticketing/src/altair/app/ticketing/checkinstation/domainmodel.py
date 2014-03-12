# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
from altair.app.ticketing.core.models import Performance, Event, Order, OrderedProductItemToken
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


from altair.app.ticketing.qr.utils import get_matched_token_query_from_order_no
from altair.app.ticketing.printqr.utils import ordered_product_item_token_query_on_organization
from altair.app.ticketing.printqr.utils import EnableTicketTemplatesCache

class ItemTokenData(object):
    def __init__(self, request, operator):
        self.request = request
        self.operator = operator

    def get_item_token_from_id(self, token_id):
        organization_id = self.operator.organization_id
        qs = ordered_product_item_token_query_on_organization(organization_id)
        return qs.filter(OrderedProductItemToken.id==token_id).first()

    def get_item_token_list_from_order_no(self, order_no):
        return get_matched_token_query_from_order_no(order_no).all()

    def get_item_token_list_from_token_id_list(self, token_id_list):
        organization_id = self.operator.organization_id
        qs = ordered_product_item_token_query_on_organization(organization_id)
        return qs.filter(OrderedProductItemToken.id.in_(token_id_list)).all()


from altair.app.ticketing.printqr import utils as p_utils
from altair.app.ticketing.printqr import todict as p_todict
from altair.app.ticketing.tickets.api import get_svg_builder


class OrderData(object):
    def __init__(self, request, operator):
        self.request = request
        self.operator = operator

    def get_order_from_order_no(self, order_no):
        ## ok?
        qs = (Order.query
              .filter_by(organization_id=self.operator.organization_id)
              .filter_by(order_no=order_no))
        return qs.first()



from altair.app.ticketing.core.utils import PrintedAtBubblingSetter
from altair.app.ticketing.models import DBSession
from altair.app.ticketing.printqr.utils import history_from_token
from altair.app.ticketing.payments.plugins import QR_DELIVERY_PLUGIN_ID

class PrintedAtUpdater(object):
    def __init__(self, request, operator):
        self.request = request
        self.operator = operator

    def update_printed_at(self, token_list, token_template_matching_dict, order, now):
        setter = PrintedAtBubblingSetter(now)

        for token in token_list:
            DBSession.add(token)

            template_id_list = token_template_matching_dict.get(unicode(token.id), [])
            for template_id in template_id_list:
                DBSession.add(history_from_token(self.request, self.operator.id, order.id, token, template_id=template_id))
            setter.printed_token(token)

        setter.start_bubbling()


class SVGDataSource(object):
    def __init__(self, request):
        self.request = request

    @reify
    def templates_cache(self):
        return EnableTicketTemplatesCache([QR_DELIVERY_PLUGIN_ID])

    def data_list_for_one(self, token):
        issuer = p_utils.get_issuer()
        svg_builder = get_svg_builder(self.request)

        vardict = p_todict.svg_data_from_token(token, issuer=issuer)
        ticket_templates = self.templates_cache(token)
        vardict["svg_list"] = svg_list_all_template_valiation(svg_builder, vardict.pop("data", {}), ticket_templates)
        return [vardict]

    def data_list_for_all(self, tokens):
        issuer = p_utils.get_issuer()
        svg_builder = get_svg_builder(self.request)

        retval = []
        for ordered_product_item_token in tokens:
            ticket_templates = self.templates_cache(ordered_product_item_token)

            vardict = p_todict.svg_data_from_token(ordered_product_item_token, issuer=issuer)
            vardict["svg_list"] = svg_list_all_template_valiation(svg_builder, vardict.pop("data", {}), ticket_templates)
            retval.append(vardict)
        return retval

from altair.app.ticketing.tickets.xaml import xaml_from_svg
def transform(svg):
    return xaml_from_svg(svg).decode("utf-8")

def svg_list_all_template_valiation(svg_builder, vardict, ticket_templates):
    ## var dictは券面のレンダリングに利用する変数のdict
    data_list = []
    for ticket_template in ticket_templates:
        data = {"svg": svg_builder.build(ticket_template, vardict, transform=transform)} 
        data[u'ticket_template_name'] = ticket_template.name
        data[u'ticket_template_id'] = unicode(ticket_template.id)
        data_list.append(data)
    return data_list
