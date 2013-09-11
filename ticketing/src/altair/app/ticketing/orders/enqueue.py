# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)

from pyramid.decorator import reify
from collections import (
    defaultdict, 
    Counter
    )
from altair.app.ticketing.core.models import orders_seat_table
from altair.app.ticketing.core.models import (
    OrderedProductItem,
    Ticket, 
    Seat,
    OrderedProductItemToken
    )
from altair.app.ticketing.core.utils import ApplicableTicketsProducer
from .utils import (
    NumberIssuer, 
    enqueue_token
    )

def get_enqueue_each_print_action(order, candidate_id_list):
    #token@seat@ordered_product_item.id@ticket.id
    if not candidate_id_list:
        return DummyEachPrintByToken(order, candidate_id_list)
    elif candidate_id_list[0][0] == None:
        return EachPrintWithoutToken(order, candidate_id_list)
    else:
        return EachPrintWithToken(order, candidate_id_list)



class DummyEachPrintByToken(object):
    def __init__(self, candidate_id_list):
        self.candidate_id_list = candidate_id_list

    def enqueue(self, operator):
        logger.warn("enqueue candidates is empty!")


def counting(xs):
    c = Counter()
    for i in xs:
        c[i] += 1
    return c

class TicketMaterialCounter(object):
    def __init__(self, candidate_id_list):
        self.candidate_id_list = candidate_id_list
        self.token_id_list, self.seat_id_list, self.ordered_product_item_id_list, self.ticket_id_list = zip(*candidate_id_list)

    @reify
    def item_children_counter(self):
        return counting(self.ordered_product_item_id_list)

    @reify
    def ordered_product_items(self):
        return OrderedProductItem.query.filter(OrderedProductItem.id.in_(self.item_children_counter.keys())).all()

    @reify
    def tokens(self):
        return OrderedProductItemToken.query.filter(OrderedProductItemToken.id.in_(self.token_id_list)).all()

    @reify
    def tickets(self):
        return Ticket.query.filter(Ticket.id.in_(self.ticket_id_list)).all()

    @reify
    def seats(self):
        return Seat.query.filter(Seat.id.in_(self.seat_id_list)).all()

class EachPrintWithToken(object):
    def __init__(self, order, candidate_id_list, mcounter_impl=TicketMaterialCounter, issuer=None):
        self.order = order
        self.mcounter = mcounter_impl(candidate_id_list)
        self.issuer = issuer or NumberIssuer()

    def enqueue(self, operator):
        mc = self.mcounter
        token_dict = {unicode(t.id):t for t in mc.tokens}
        seat_dict = {unicode(s.id):s for s in mc.seats}
        ticket_dict ={unicode(t.id):t for t in mc.tickets}
        item_dict = {unicode(i.id):i for i in mc.ordered_product_items}

        counter = Counter()
        for token_id, seat_id, ticket_id in zip(mc.token_id_list, mc.seat_id_list, mc.ticket_id_list):
            token = token_dict[token_id]
            ticket = ticket_dict[ticket_id]
            k = unicode(token.ordered_product_item_id)

            counter[k] += 1
            i = counter[k]
            j = mc.item_children_counter[k]
            ordered_product_item = item_dict[k]
            enqueue_token(operator, token, ticket, i, j, 
                          ordered_product_item=ordered_product_item, order=self.order,
                          seat=seat_dict.get(seat_id), issuer=self.issuer)
            
class EachPrintWithoutToken(object):
    def __init__(self, order, candidate_id_list, mcounter_impl=TicketMaterialCounter, issuer=None):
        self.order = order
        self.mcounter = mcounter_impl(candidate_id_list)
        self.issuer = issuer or NumberIssuer()

    def _with_serial_and_seat(self, ordered_product,  ordered_product_item):
        if ordered_product_item.seats:
            for i, s in enumerate(ordered_product_item.seats):
                yield i, s
        else:
            for i in xrange(ordered_product.quantity):
                yield i, None

    def generate_tokens(self):
        order = self.order
        using_tokens = defaultdict(list)
        seats = set(self.mcounter.seat_id_list)
        opis = set(self.mcounter.ordered_product_item_id_list)
        opi_count = self.mcounter.item_children_counter
        for op in order.ordered_products:
            for opi in op.ordered_product_items:
                for i, seat in self._with_serial_and_seat(op, opi):
                    token = OrderedProductItemToken(
                        item = opi, 
                        serial = i, 
                        seat = seat, 
                        valid=True
                        )
                    opi.tokens.append(token)
                    if seat:
                        if unicode(seat.id) in seats:
                            using_tokens[(unicode(opi.id), unicode(seat.id))].append(token)
                    else:
                        if unicode(opi.id) in opis and opi_count.get(unicode(opi.id)) > i:
                            using_tokens[(unicode(opi.id), unicode(None))].append(token)
        return using_tokens

    def enqueue(self, operator):
        token_list_dict = self.generate_tokens()
        return self._enqueue(operator, token_list_dict)

    def _enqueue(self, operator, token_list_dict):
        counter = Counter()

        mc = self.mcounter
        ticket_dict ={unicode(t.id):t for t in mc.tickets}
        seat_dict = {unicode(s.id):s for s in mc.seats}
        item_dict = {unicode(i.id):i for i in mc.ordered_product_items}

        ticket_use_counter = Counter()
        for item_id, seat_id, ticket_id in zip(mc.ordered_product_item_id_list, mc.seat_id_list, mc.ticket_id_list):
            ticket = ticket_dict[ticket_id]
            sub = (unicode(item_id), unicode(seat_id))
            tri = (unicode(item_id), unicode(seat_id), unicode(ticket_id))
            i = ticket_use_counter[tri]
            token = token_list_dict[sub][i]
            ticket_use_counter[tri] += 1

            counter[item_id] += 1
            i = counter[item_id]
            j = mc.item_children_counter[item_id]

            ordered_product_item = item_dict[item_id]
            enqueue_token(operator, token, ticket, i, j, 
                          ordered_product_item=ordered_product_item, order=self.order,
                          seat=seat_dict.get(seat_id), issuer=self.issuer)

##
class JoinedObjectsForProductItemDependentsProvider(object):
    def __init__(self, objs):
        self.objs = objs

    @property
    def ordered_product_item_id_list(self):
        return [os[1].id for os in self.objs]

    @property
    def ordered_product_item_list(self):
        return [os[1] for os in self.objs]

    def __call__(self):
        if not self.objs:
            return self.objs
        if self.hasnt_token():
            return self.objects_for_product_item_without_token()
        else:
            return self.objects_for_product_item_with_token()

    def hasnt_token(self):
        return self.objs[0][-1] is None

    def get_product_item_attributes(self, metadata_provider_registry):
        ordered_product_items = self.ordered_product_item_list
        ordered_product_attributes = []
        for key, value in (
            pair
            for ordered_product_item in ordered_product_items
            for pair in ordered_product_item.attributes.items()):
            metadata = None
            try:
                metadata = metadata_provider_registry.queryProviderByKey(key)[key]
            except:
                pass
            if metadata is not None:
                display_name = metadata.get_display_name('ja_JP')
                coerced_value = metadata.get_coercer()(value)
            else:
                display_name = key
                coerced_value = value

            ordered_product_attributes.append((display_name, key, coerced_value))
        ordered_product_attributes = sorted(ordered_product_attributes, key=lambda x: x[0])
        return ordered_product_attributes

    def objects_for_product_item_with_token(self):
        "[(ordered_product, [(OrderedproductItem, ((seat , token_id), [ticket, ...]), ...), ...])]"
        ticket_cache = defaultdict(list)
        parent_product, parent_item = None, None
        r = []
        item_list = []
        seat_list = []
        for ordered_product, ordered_product_item, product_item, ticket_bundle, seat, token in self.objs:
            if ordered_product != parent_product:
                parent_product = ordered_product
                item_list = []
                r.append((parent_product, item_list))
            if ordered_product_item != parent_item:
                parent_item = ordered_product_item
                seat_list = []
                item_list.append((parent_item, seat_list))
            if not ticket_bundle.id in ticket_cache:
                ticket_cache[ticket_bundle.id] = list(ApplicableTicketsProducer.from_bundle(ticket_bundle).will_issued_by_own_tickets())
            seat_list.append(((seat, token), ticket_cache[ticket_bundle.id]))
        return r


    def objects_for_product_item_without_token(self):
        "[(ordered_product, [(OrderedproductItem, ((seat , token_id), [ticket, ...]), ...), ...])]"
        ordered_items_id = [os[1].id for os in self.objs]
        seats = Seat.query.join(orders_seat_table, orders_seat_table.c.seat_id==Seat.id)
        seats = seats.filter(orders_seat_table.c.OrderedProductItem_id.in_(ordered_items_id))
        seat_dict = defaultdict(list)
        for id, seat in seats.with_entities(orders_seat_table.c.OrderedProductItem_id, Seat).all():
            seat_dict[id].append(seat)
        ticket_cache = defaultdict(list)

        parent_product, parent_item = None, None
        r = []
        item_list = []
        seat_list = []
        for ordered_product, ordered_product_item, product_item, ticket_bundle, _, _ in self.objs:
            if ordered_product != parent_product:
                parent_product = ordered_product
                item_list = []
                r.append((parent_product, item_list))
            if ordered_product_item != parent_item:
                parent_item = ordered_product_item
                seat_list = []
                item_list.append((parent_item, seat_list))
            seats = seat_dict.get(ordered_product_item.id, None)
            if seats is None:
                for i in range(parent_item.quantity):
                    if ticket_bundle is None:
                        tickets = []
                    else:
                        if not ticket_bundle.id in ticket_cache:
                            ticket_cache[ticket_bundle.id] = list(ApplicableTicketsProducer.from_bundle(ticket_bundle).will_issued_by_own_tickets())
                        tickets = ticket_cache[ticket_bundle.id]
                    seat_list.append(((None, None), tickets))
            else:
                for seat in seats:
                    if ticket_bundle is None:
                        tickets = []
                    else:
                        if not ticket_bundle.id in ticket_cache:
                            ticket_cache[ticket_bundle.id] = list(ApplicableTicketsProducer.from_bundle(ticket_bundle).will_issued_by_own_tickets())
                        tickets = ticket_cache[ticket_bundle.id]
                    seat_list.append(((seat, None), tickets))
        return r

