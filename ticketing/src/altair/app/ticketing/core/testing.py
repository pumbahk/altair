# encoding: utf-8

from decimal import Decimal

class CoreTestMixin(object):
    def setUp(self):
        from altair.app.ticketing.core.models import (
            Organization,
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
        self.organization = Organization(id=1, short_name=u'')
        self.event = Event(organization=self.organization, title=u'イベント')
        self.performance = Performance(
            event=self.event,
            venue=Venue(organization=self.organization, site=Site()),
            name=u'パフォーマンス'
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
                            name=name, fee=Decimal(0.),
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
        from altair.app.ticketing.core.models import StockType
        return [StockType(name=name) for name in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'[0:num]]

    def _create_stocks(self, stock_types):
        from altair.app.ticketing.core.models import Stock, StockStatus, StockHolder, Performance, Venue, Site
        quantity = 4
        return [Stock(performance=self.performance, stock_type=stock_type, quantity=quantity, stock_holder=StockHolder(name='holder of %s' % stock_type.name), stock_status=StockStatus(quantity=quantity)) for stock_type in stock_types]

    def _create_seats(self, stocks):
        from altair.app.ticketing.core.models import Seat, SeatStatus, SeatStatusEnum
        return [Seat(name=u"Seat %s-%d" % (stock.stock_type.name, i),
                     l0_id="seat-%s-%d" % (stock.stock_type.name, i),
                     stock=stock,
                     venue=stock.performance and stock.performance.venue,
                     status_=SeatStatus(status=SeatStatusEnum.Vacant.v)) \
                for stock in stocks for i in range(stock.quantity)]

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
                Ticket(ticket_format=ticket_format, flags=Ticket.FLAG_PRICED)
                for ticket_format in self._generate_ticket_formats()
                ]
            )
 
    def _create_products(self, stocks):
        from altair.app.ticketing.core.models import Product, ProductItem
        price = Decimal(100.)
        return [
            Product(
                name=stock.stock_type.name,
                price=price,
                performance=self.performance, 
                items=[ProductItem(stock=stock, price=price,
                                   performance=self.performance,
                                   quantity=1,
                                   ticket_bundle=self._create_ticket_bundle())]
                )
            for stock in stocks
            ]

    def _create_payment_delivery_method_pairs(self, sales_segment_group, system_fee=0., system_fee_type=0, transaction_fee=0., delivery_fee=0., special_fee=0, special_fee_type=0, discount=0., discount_unit=0):
        from altair.app.ticketing.core.models import PaymentDeliveryMethodPair
        return [
            PaymentDeliveryMethodPair(
                sales_segment_group=sales_segment_group,
                system_fee=Decimal(system_fee),
                system_fee_type=system_fee_type,
                transaction_fee=Decimal(transaction_fee),
                delivery_fee=Decimal(delivery_fee),
                special_fee=Decimal(special_fee),
                special_fee_type=special_fee_type,
                discount=Decimal(discount),
                discount_unit=discount_unit,
                public=True,
                payment_method=payment_method,
                delivery_method=delivery_method,
                issuing_interval_days=5
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
            address_1=u"東五反田5-21-15'",
            address_2=u"メタリオンOSビル",
            tel_1=u"03-9999-9999",
            tel_2=u"090-0000-0000",
            fax=u"03-9876-5432"
            )

    def _pick_seats(self, stock, quantity):
        from altair.app.ticketing.core.models import Seat, SeatStatus, SeatStatusEnum
        return [Seat(
            name='seat',
            l0_id='seat',
            venue=stock.performance and stock.performance.venue,
            status_=SeatStatus(status=SeatStatusEnum.InCart.v))
            ]

    def _create_order(self, product_quantity_pairs, sales_segment=None, pdmp=None):
        from altair.app.ticketing.core.models import Order, OrderedProduct, OrderedProductItem, SeatStatusEnum, FeeTypeEnum, Ticket

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
                seats = [ 
                    mark_ordered(seat)
                    for seat in self._pick_seats(product_item.stock, quantity * product_item.quantity)
                    ]
                ordered_product_item = OrderedProductItem(
                    product_item=product_item,
                    price=product_item.price,
                    seats=seats,
                    quantity=len(seats)
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
                    int((ticket.flags & Ticket.FLAG_PRICED) and (pdmp.delivery_method in ticket.ticket_format.delivery_methods))
                    for ticket in ordered_product_item.product_item.ticket_bundle.tickets
                    )
                for ordered_product in items
                for ordered_product_item in ordered_product.elements)
            system_fee = pdmp.system_fee if pdmp.system_fee_type == FeeTypeEnum.Once.v[0] else pdmp.system_fee * num_tickets
            special_fee = pdmp.special_fee if pdmp.special_fee_type == FeeTypeEnum.Once.v[0] else pdmp.special_fee * num_tickets
        else:
            system_fee = Decimal()
            special_fee = Decimal()

        return Order(
            organization_id=self.organization.id,
            shipping_address=self._create_shipping_address(),
            total_amount=sum(product.price for product, _ in product_quantity_pairs),
            payment_delivery_pair=pdmp,
            sales_segment=sales_segment,
            system_fee=Decimal(system_fee),
            transaction_fee=Decimal(pdmp and pdmp.transaction_fee or 0.),
            delivery_fee=Decimal(pdmp and pdmp.delivery_fee or 0.),
            special_fee=Decimal(special_fee),
            issued=False,
            items=items,
            performance=performance
            )

