# encoding: utf-8

from decimal import Decimal
from datetime import datetime

class CoreTestMixin(object):
    def setUp(self):
        from altair.app.ticketing.core.models import (
            Organization,
            Host,
            Event,
            Performance,
            Site,
            Venue,
            PaymentMethod,
            DeliveryMethod,
            PaymentMethodPlugin,
            DeliveryMethodPlugin
            )
        from altair.app.ticketing.payments import plugins as _payment_plugins
        import re
        from datetime import datetime
        self.organization = Organization(id=1, short_name=u'', code=u'XX')
        self.host = Host(organization=self.organization, host_name='example.com:80')
        self.event = Event(organization=self.organization, title=u'イベント')
        self.performance = Performance(
            start_on=datetime(1970, 1, 1),
            event=self.event,
            venue=Venue(organization=self.organization, site=Site()),
            name=u'パフォーマンス',
            code=u'ABCDEFGH'
            )
        payment_methods = {}
        delivery_methods = {}
        for attr_name in dir(_payment_plugins):
            g = re.match(ur'^(.*)_PAYMENT_PLUGIN_ID$', attr_name)
            if g:
                id = getattr(_payment_plugins, attr_name)
                name = g.group(1)
                payment_methods[id] = \
                    PaymentMethod(
                        name=name, fee=Decimal(0.),
                        organization=self.organization,
                        payment_plugin_id=id,
                        _payment_plugin=PaymentMethodPlugin(id=id, name=name)
                        )
            else:
                g = re.match(ur'^(.*)_DELIVERY_PLUGIN_ID$', attr_name)
                if g:
                    id = getattr(_payment_plugins, attr_name)
                    name = g.group(1)
                    delivery_methods[id] = \
                        DeliveryMethod(
                            name=name,
                            fee_per_order=Decimal(0.),
                            fee_per_principal_ticket=Decimal(0.),
                            fee_per_subticket=Decimal(0.),
                            organization=self.organization,
                            delivery_plugin_id=id,
                            _delivery_plugin=DeliveryMethodPlugin(id=id, name=name)
                            )
        self.payment_methods = payment_methods
        self.delivery_methods = delivery_methods
        self.order_no_list = []

    def new_order_no(self):
        order_no = '%012d' % len(self.order_no_list)
        self.order_no_list.append(order_no)
        return order_no

    def _create_stock_types(self, num):
        from altair.app.ticketing.core.models import StockType, StockTypeEnum
        return [
            StockType(
                name=name,
                type=(StockTypeEnum.Seat.v if i % 3 < 2 else StockTypeEnum.Other.v),
                quantity_only=(i % 3 > 0)
                )
            for i, name in enumerate('ABCDEFGHIJKLMNOPQRSTUVWXYZ'[0:num])
            ]

    def _create_stocks(self, stock_types, quantity=4):
        from altair.app.ticketing.core.models import Stock, StockStatus, StockHolder, Performance, Venue, Site
        return [Stock(performance=self.performance, stock_type=stock_type, quantity=quantity, stock_holder=StockHolder(name='holder of %s' % stock_type.name), stock_status=StockStatus(quantity=quantity)) for stock_type in stock_types]

    def _create_stocks_from_pairs(self, stock_type_quantity_pairs):
        from altair.app.ticketing.core.models import Stock, StockStatus, StockHolder, Performance, Venue, Site
        return [Stock(performance=self.performance, stock_type=stock_type, quantity=quantity, stock_holder=StockHolder(name='holder of %s' % stock_type.name), stock_status=StockStatus(quantity=quantity)) for stock_type, quantity in stock_type_quantity_pairs]

    def _create_seats(self, stocks):
        from altair.app.ticketing.core.models import Seat, SeatStatus, SeatStatusEnum, SeatIndexType, SeatIndex
        retval = []
        for stock in stocks:
            venue = stock.performance and stock.performance.venue
            seat_index_type = SeatIndexType(venue=venue, name=stock.stock_type.name)
            if not stock.stock_type.quantity_only:
                for i in range(stock.quantity):
                    retval.append(
                        Seat(
                            name=u"Seat %s-%d" % (stock.stock_type.name, i),
                            l0_id="seat-%s-%d" % (stock.stock_type.name, i),
                            stock=stock,
                            venue=venue,
                            status_=SeatStatus(status=SeatStatusEnum.Vacant.v),
                            indexes=[SeatIndex(seat_index_type=seat_index_type, index=0)]
                            )
                        )
        return retval

    def _create_seat_adjacency_sets(self, seats):
        from altair.app.ticketing.core.models import SeatAdjacencySet, SeatAdjacency
        seats_for_site_map = {}
        for seat in seats:
            seats_for_site = seats_for_site_map.get(seat.venue.site)
            if seats_for_site is None:
                seats_for_site = seats_for_site_map[seat.venue.site] = []
            seats_for_site.append(seat)

        return sum(
            (
                [
                    SeatAdjacencySet(
                        site=site,
                        seat_count=i,
                        adjacencies=[
                            SeatAdjacency(seats=seats_for_site[j:j + i])
                            for j in range(0, len(seats_for_site) + 1 - i)
                            ]
                        )
                    for i in range(2, len(seats_for_site) + 1)
                    ]
                for site, seats_for_site in seats_for_site_map.items()
                ),
            []
            )

    def _create_ticket_format(self, name='ticket_format', delivery_methods=None):
        from altair.app.ticketing.core.models import TicketFormat
        return TicketFormat(
            name=name,
            delivery_methods=delivery_methods,
            data={
                u'print_offset': { u'x': u'0', u'y': u'0' }
                }
            )

    def _generate_ticket_formats(self):
        from itertools import combinations
        for n in range(1, len(self.delivery_methods)):
            for j, combination in enumerate(combinations(self.delivery_methods.values(), n)):
                yield self._create_ticket_format(
                    name='%d-%d' % (n, j),
                    delivery_methods=list(combination),
                    )

    def _create_ticket_bundle(self):
        from altair.app.ticketing.core.models import TicketBundle, Ticket
        return TicketBundle(
            tickets=[
                Ticket(ticket_format=ticket_format, flags=Ticket.FLAG_PRINCIPAL)
                for ticket_format in self._generate_ticket_formats()
                ]
            )

    def _create_products(self, stocks, sales_segment=None):
        from altair.app.ticketing.core.models import Product, ProductItem
        price = Decimal(100.)
        return [
            Product(
                name=stock.stock_type.name,
                price=price,
                performance=self.performance,
                sales_segment=sales_segment,
                items=[
                    ProductItem(
                        name=u'product_item_of_%s' % stock.stock_type.name,
                        stock=stock,
                        price=price,
                        performance=self.performance,
                        quantity=1,
                        ticket_bundle=self._create_ticket_bundle()
                        )
                    ]
                )
            for stock in stocks
            ]

    def _create_payment_delivery_method_pairs(self, sales_segment_group, system_fee=0., system_fee_type=0, transaction_fee=0., delivery_fee_per_order=0., delivery_fee_per_principal_ticket=0., delivery_fee_per_subticket=0., special_fee=0, special_fee_type=0, discount=0., discount_unit=0):
        import datetime
        from altair.app.ticketing.core.models import (
            PaymentDeliveryMethodPair,
            DateCalculationBase,
            )

        return [
            PaymentDeliveryMethodPair(
                sales_segment_group=sales_segment_group,
                system_fee=Decimal(system_fee),
                system_fee_type=system_fee_type,
                transaction_fee=Decimal(transaction_fee),
                delivery_fee_per_order=Decimal(delivery_fee_per_order),
                delivery_fee_per_principal_ticket=Decimal(delivery_fee_per_principal_ticket),
                delivery_fee_per_subticket=Decimal(delivery_fee_per_subticket),
                special_fee=Decimal(special_fee),
                special_fee_type=special_fee_type,
                discount=Decimal(discount),
                discount_unit=discount_unit,
                public=True,
                payment_method=payment_method,
                delivery_method=delivery_method,
                payment_start_day_calculation_base=DateCalculationBase.OrderDate.v,
                payment_start_in_days=0,
                payment_due_day_calculation_base=DateCalculationBase.OrderDate.v,
                payment_period_days=3,
                issuing_start_day_calculation_base=DateCalculationBase.OrderDate.v,
                issuing_interval_days=5,
                issuing_end_day_calculation_base=DateCalculationBase.OrderDate.v,
                issuing_end_in_days=364,
                )
            for payment_method in self.payment_methods.values()
            for delivery_method in self.delivery_methods.values()
            ]

    def _create_shipping_address(self):
        from .models import ShippingAddress
        return ShippingAddress(
            email_1="dev+test000@ticketstar.jp",
            email_2="dev+mobile-test000@ticketstar.jp",
            first_name=u"太郎0",
            last_name=u"楽天",
            first_name_kana=u"タロウ",
            last_name_kana=u"ラクテン",
            zip="251-0036",
            prefecture=u"東京都",
            city=u"品川区",
            address_1=u"東五反田5-21-15",
            address_2=u"メタリオンOSビル",
            tel_1=u"03-9999-9999",
            tel_2=u"090-0000-0000",
            fax=u"03-9876-5432"
            )

    def _pick_seats(self, stock, quantity):
        # XXX: THIS IS THE DEFAULT IMPLEMENTATION. PLEASE OVERRIDE THIS.
        from altair.app.ticketing.core.models import Seat, SeatStatus, SeatStatusEnum
        return [
            Seat(
                name='seat',
                l0_id='seat',
                venue=(stock.performance and stock.performance.venue),
                status_=SeatStatus(status=SeatStatusEnum.Vacant.v)
                )
            for _ in range(quantity)
            ]

    def _create_order(self, product_quantity_pairs, sales_segment=None, pdmp=None, order_no=None, cart_setting_id=None):
        from altair.app.ticketing.core.models import SeatStatusEnum, FeeTypeEnum, Ticket, StockTypeEnum
        from altair.app.ticketing.orders.models import Order, OrderedProduct, OrderedProductItem, OrderedProductItemToken

        if order_no is None:
            order_no = self.new_order_no()

        def mark_ordered(seat):
            seat.status = SeatStatusEnum.Ordered.v
            return seat

        items = []
        performance = None
        for product, quantity in product_quantity_pairs:
            elements = []

            if performance is not None:
                assert performance == product.performance
            performance = product.performance

            for product_item in product.items:
                product_item_quantity = quantity * product_item.quantity
                if not product_item.stock.stock_type.quantity_only:
                    seats = [
                        mark_ordered(seat)
                        for seat in self._pick_seats(product_item.stock, product_item_quantity)
                        ]
                    tokens = [
                        OrderedProductItemToken(
                            seat=seat,
                            serial=(i + 1),
                            valid=True
                            )
                        for i, seat in enumerate(seats)
                        ]
                else:
                    seats = []
                    tokens = [
                        OrderedProductItemToken(serial=(i + 1), valid=True)
                        for i in range(0, product_item_quantity)
                        ]

                ordered_product_item = OrderedProductItem(
                    product_item=product_item,
                    price=product_item.price,
                    seats=seats,
                    tokens=tokens,
                    quantity=product_item_quantity
                    )
                elements.append(ordered_product_item)
            ordered_product = OrderedProduct(
                product=product, quantity=quantity,
                price=product.price,
                ordered_product_items=elements
                )
            items.append(ordered_product)
        if pdmp:
            num_tickets = sum(
                ordered_product_item.quantity * sum(
                    int((ticket.flags & Ticket.FLAG_PRINCIPAL) and (pdmp.delivery_method in ticket.ticket_format.delivery_methods))
                    for ticket in ordered_product_item.product_item.ticket_bundle.tickets
                    )
                for ordered_product in items
                for ordered_product_item in ordered_product.elements)
            system_fee = Decimal(pdmp.system_fee if pdmp.system_fee_type == FeeTypeEnum.Once.v[0] else pdmp.system_fee * num_tickets)
            special_fee = Decimal(pdmp.special_fee if pdmp.special_fee_type == FeeTypeEnum.Once.v[0] else pdmp.special_fee * num_tickets)
        else:
            system_fee = Decimal()
            special_fee = Decimal()
        transaction_fee = Decimal(pdmp and pdmp.transaction_fee or 0.)
        delivery_fee = Decimal(pdmp and pdmp.delivery_fee or 0.)
        special_fee = Decimal(special_fee)
        total_amount = Decimal(sum(product.price * quantity for product, quantity in product_quantity_pairs)) + transaction_fee + delivery_fee + special_fee

        if cart_setting_id is None:
            try:
                if performance is not None and performance.event is not None and performance.event.setting is not None:
                    cart_setting_id = performance.event.setting.cart_setting_id
                else:
                    cart_setting_id = self.organization.setting.cart_setting_id
            except:
                pass
        return Order(
            order_no=order_no,
            organization_id=self.organization.id,
            shipping_address=self._create_shipping_address(),
            total_amount=total_amount,
            payment_delivery_pair=pdmp,
            sales_segment=sales_segment,
            system_fee=system_fee,
            transaction_fee=transaction_fee,
            delivery_fee=delivery_fee,
            special_fee=special_fee,
            issuing_start_at=datetime(1970, 1, 1),
            issuing_end_at=datetime(1970, 1, 1),
            payment_start_at=datetime(1970, 1, 1),
            payment_due_at=datetime(1970, 1, 1),
            issued=False,
            items=items,
            performance=performance,
            cart_setting_id=cart_setting_id
            )
