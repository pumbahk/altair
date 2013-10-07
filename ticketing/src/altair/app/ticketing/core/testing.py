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
        self.organization = Organization(short_name=u'')
        self.event = Event(organization=self.organization)
        self.performance = Performance(event=self.event, venue=Venue(organization=self.organization, site=Site()))
        payment_methods = {}
        delivery_methods = {}
        for attr_name in dir(_payment_plugins):
            g = re.match(ur'^(.*)_PAYMENT_PLUGIN_ID$', attr_name)
            if g:
                id = getattr(_payment_plugins, attr_name)
                name = g.group(1)
                payment_methods[id] = \
                    PaymentMethod(
                        name=name, fee=0.,
                        organization=self.organization,
                        _payment_plugin=PaymentMethodPlugin(id=id, name=name)
                        )
            else:
                g = re.match(ur'^(.*)_DELIVERY_PLUGIN_ID$', attr_name)
                if g:
                    id = getattr(_payment_plugins, attr_name)
                    name = g.group(1)
                    delivery_methods[id] = \
                        DeliveryMethod(
                            name=name, fee=0.,
                            organization=self.organization,
                            _delivery_plugin=DeliveryMethodPlugin(id=id, name=name)
                            )
        self.payment_methods = payment_methods
        self.delivery_methods = delivery_methods


    def _create_stock_types(self, num):
        from altair.app.ticketing.core.models import StockType
        return [StockType(name=name) for name in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'[0:num]]

    def _create_stocks(self, stock_types):
        from altair.app.ticketing.core.models import Stock, StockStatus, Performance, Venue, Site
        quantity = 4
        return [Stock(performance=self.performance, stock_type=stock_type, quantity=quantity, stock_status=StockStatus(quantity=quantity)) for stock_type in stock_types]

    def _create_seats(self, stocks):
        from altair.app.ticketing.core.models import Seat, SeatStatus, SeatStatusEnum
        return [Seat(name=u"Seat %s-%d" % (stock.stock_type.name, i),
                     l0_id="seat-%s-%d" % (stock.stock_type.name, i),
                     stock=stock,
                     venue=stock.performance and stock.performance.venue,
                     status_=SeatStatus(status=SeatStatusEnum.InCart.v)) \
                for stock in stocks for i in range(stock.quantity)]

    def _create_ticket_bundle(self):
        from itertools import combinations
        from altair.app.ticketing.core.models import TicketBundle, Ticket, TicketFormat
        return TicketBundle(
            tickets=[
                Ticket(
                    ticket_format=TicketFormat(
                        name='%d-%d' % (n, j),
                        delivery_methods=list(combination),
                        ),
                    flags=Ticket.FLAG_PRICED
                    )
                for n in range(1, len(self.delivery_methods))
                for j, combination in enumerate(combinations(self.delivery_methods.values(), n))
                ]
            )
 
    def _create_products(self, stocks):
        from altair.app.ticketing.core.models import Product, ProductItem
        price = 100.
        return [
            Product(
                name=stock.stock_type.name,
                price=price,
                items=[ProductItem(stock=stock, price=price,
                                   ticket_bundle=self._create_ticket_bundle())]
                )
            for stock in stocks
            ]

    def _create_payment_delivery_method_pairs(self, sales_segment_group, system_fee=0., transaction_fee=0., delivery_fee=0., discount=0., discount_unit=0):
        from altair.app.ticketing.core.models import PaymentDeliveryMethodPair
        return [
            PaymentDeliveryMethodPair(
                sales_segment_group=sales_segment_group,
                system_fee=system_fee,
                transaction_fee=transaction_fee,
                delivery_fee=delivery_fee,
                discount=discount,
                discount_unit=discount_unit,
                public=True,
                payment_method=payment_method,
                delivery_method=delivery_method
                )
            for payment_method in self.payment_methods.values()
            for delivery_method in self.delivery_methods.values()
            ]

    def _create_order(self, product_quantity_pairs, pdmp=None):
        from altair.app.ticketing.core.models import Order, OrderedProduct, OrderedProductItem, SeatStatusEnum

        def mark_ordered(seat):
            seat.status = SeatStatusEnum.Ordered.v
            return seat

        return Order(
            organization_id=self.organization.id,
            total_amount=sum(product.price for product, _ in product_quantity_pairs),
            payment_delivery_pair=pdmp,
            system_fee=pdmp and pdmp.system_fee or 0.,
            transaction_fee=pdmp and pdmp.transaction_fee or 0.,
            delivery_fee=pdmp and pdmp.delivery_fee or 0.,
            issued=False,
            items=[
                OrderedProduct(
                    product=product, quantity=quantity,
                    price=product.price,
                    ordered_product_items=[
                        OrderedProductItem(
                            product_item=product_item,
                            price=product_item.price,
                            seats=[
                                mark_ordered(seat)
                                for seat in self._create_seats([product_item.stock])
                                ]
                            )
                        for product_item in product.items
                        ]
                    )
                for product, quantity in product_quantity_pairs
                ]
            )
