import unittest
import mock
from functools import partial
from pyramid.testing import DummyResource as O

class FakeMaterialCounter(object): 
    """token@seat@ordered_product_item.id@ticket.id"""
    def __init__(self, candidate_id_list, ordered_product_items=[], tokens=[], tickets=[], seats=[], item_children_counter={}):
        self.token_id_list, self.seat_id_list, self.ordered_product_item_id_list, self.ticket_id_list = zip(*candidate_id_list)
        self.ordered_product_items = ordered_product_items
        self.tokens = tokens
        self.tickets = tickets
        self.seats = seats
        self.item_children_counter = item_children_counter

OrderedProduct = partial(O, name="ordered_product")
OrderedProductItem = OPI = partial(O, name="ordered_product_item")
ProductItem = partial(O, name="product_item")
TicketBundle = partial(O, name="ticket_bundle")
OrderedProductItemToken = Token = partial(O, name="token")
Ticket = partial(O, name="ticket")
Seat = partial(O, name="seat")
Order = partial(O, name="order")
Operator = partial(O, name="operator")

class DummyTicketsProducer(object):
    def __init__(self, bundle, tickets):
        self.bundle = bundle 
        self.tickets = tickets

    def will_issued_by_own_tickets(self):
        return self.tickets

class DescribeProductItemTreeTests(unittest.TestCase):
    def _getTarget(self):
        from altair.app.ticketing.orders.enqueue import JoinedObjectsForProductItemDependentsProvider
        return JoinedObjectsForProductItemDependentsProvider

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_with_token(self):
        bundle = TicketBundle(id="bundle1")
        ordered_product = OrderedProduct()
        ordered_product_item = OrderedProductItem()
        product_item = ProductItem()
        objs = [(ordered_product, ordered_product_item, product_item, bundle, Seat(), OrderedProductItemToken()), 
                (ordered_product, ordered_product_item, product_item, bundle, Seat(), OrderedProductItemToken()), 
                ]
        target = self._makeOne(objs)
        tickets = [Ticket(), Ticket()]

        fake_producer = DummyTicketsProducer(bundle, tickets)
        with mock.patch("altair.app.ticketing.orders.enqueue.ApplicableTicketsProducer") as m:
            def from_bundle(ticket_bundle):
                self.assertEqual(ticket_bundle, bundle)
                return fake_producer
            m.from_bundle.side_effect = partial(from_bundle)

            result = target.objects_for_product_item_with_token()

            """
            [(<OrderedProduct 0x30743b0>,
              [(<OrderedProductItem 0x30743f8>,
                [((<Seat 0x3074488>, <Token 0x30744d0>), [<Ticket 0x307e200>, <Ticket 0x307b5f0>]),
                ((<Seat 0x3074518>, <Token 0x3074560>), [<Ticket 0x307e200>, <Ticket 0x307b5f0>])])])]
            """
            for op, item_list in result:
                self.assertEquals(op, ordered_product)
                for opi, seat_list in item_list:
                    self.assertEquals(opi, ordered_product_item)
                    for (seat, token), ticket_list in seat_list:
                        self.assertEquals(seat.name, "seat")
                        self.assertEquals(token.name, "token")
                        self.assertEquals(ticket_list, tickets)

    def test_without_token(self):
        bundle = TicketBundle(id="bundle1")
        ordered_product = OrderedProduct()
        ordered_product_item = OrderedProductItem()
        product_item = ProductItem()
        objs = [(ordered_product, ordered_product_item, product_item, bundle, None, None), 
                (ordered_product, ordered_product_item, product_item, bundle, None, None), 
                ]
        target = self._makeOne(objs)
        tickets = [Ticket(), Ticket()]

        fake_producer = DummyTicketsProducer(bundle, tickets)
        with mock.patch("altair.app.ticketing.orders.enqueue.ApplicableTicketsProducer") as m:
            def from_bundle(ticket_bundle):
                self.assertEqual(ticket_bundle, bundle)
                return fake_producer
            m.from_bundle.side_effect = partial(from_bundle)

            result = target.objects_for_product_item_with_token()

            """
            [(<OrderedProduct 0x30743b0>,
              [(<OrderedProductItem 0x30743f8>,
                [((None, None), [<Ticket 0x307e200>, <Ticket 0x307b5f0>]),
                 ((None, None), [<Ticket 0x307e200>, <Ticket 0x307b5f0>])])])]
            """
            for op, item_list in result:
                self.assertEquals(op, ordered_product)
                for opi, seat_list in item_list:
                    self.assertEquals(opi, ordered_product_item)
                    for (seat, token), ticket_list in seat_list:
                        self.assertIsNone(seat)
                        self.assertIsNone(token)
                        self.assertEquals(ticket_list, tickets)


class EnqueueWithTokenTests(unittest.TestCase):
    def _getTarget(self):
        from altair.app.ticketing.orders.enqueue import EachPrintWithToken
        return EachPrintWithToken

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_with_seat(self):
        candidate_id_list = [x.split("@") for x in ["token1@seat1@item1@ticket1", "token2@seat2@item1@ticket1"]]
        mcounter_impl = partial(FakeMaterialCounter, 
                                ordered_product_items=[OPI(id="item1")], 
                                tokens=[Token(id="token2", ordered_product_item_id="item1"), Token(id="token1", ordered_product_item_id="item1")], 
                                tickets=[Ticket(id="ticket1")], 
                                seats=[Seat(id="seat1"), Seat(id="seat2")], 
                                item_children_counter={"item1": 2})
        order = Order()
        target = self._makeOne(order, candidate_id_list, mcounter_impl=mcounter_impl, issuer="issuer")
        D = target.mcounter
        operator = Operator()
        with mock.patch("altair.app.ticketing.orders.enqueue.enqueue_token", autospec=True) as m:
            target.enqueue(operator)
            m.assert_has_calls([mock.call(operator, D.tokens[1], D.tickets[0], 1, 2, 
                                          **{"ordered_product_item":D.ordered_product_items[0], "order": order, "seat":D.seats[0], "issuer":"issuer"}), 
                                mock.call(operator, D.tokens[0], D.tickets[0], 2, 2,
                                          **{"ordered_product_item":D.ordered_product_items[0], "order": order, "seat":D.seats[1], "issuer":"issuer"})])

    def test_without_seat(self):
        candidate_id_list = [["token1", None, "item1", "ticket1"]]
        mcounter_impl = partial(FakeMaterialCounter, 
                                ordered_product_items=[OPI(id="item1")], 
                                tokens=[Token(id="token1", ordered_product_item_id="item1")], 
                                tickets=[Ticket(id="ticket1")], 
                                seats=[], 
                                item_children_counter={"item1": 1})
        order = Order()
        target = self._makeOne(order, candidate_id_list, mcounter_impl=mcounter_impl, issuer="issuer")
        D = target.mcounter
        operator = Operator()
        with mock.patch("altair.app.ticketing.orders.enqueue.enqueue_token", autospec=True) as m:
            target.enqueue(operator)
            m.assert_has_calls([mock.call(operator, D.tokens[0], D.tickets[0], 1, 1, 
                                               **{"ordered_product_item":D.ordered_product_items[0], "order": order, "seat":None, "issuer":"issuer"})])

class EnqueueWithoutTokenTests(unittest.TestCase):
    def _getTarget(self):
        from altair.app.ticketing.orders.enqueue import EachPrintWithoutToken
        return EachPrintWithoutToken

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_generate_with_seat(self):
        candidate_id_list = [[None, "seat1", "item1", "ticket1"], [None, "seat2", "item1", "ticket1"]]
        seat1 = Seat(id="seat1")
        seat2 = Seat(id="seat2")
        seat3 = Seat(id="seat3")

        item = OPI(id="item1", seats=[seat3, seat1, seat2], tokens=[])
        order = Order(ordered_products=[])
        ordered_product = O(name="op", ordered_product_items=[])
        order.ordered_products.append(ordered_product)
        ordered_product.ordered_product_items.append(item)

        mcounter_impl = partial(FakeMaterialCounter, 
                                ordered_product_items=[item], 
                                tickets=[Ticket(id="ticket1")], 
                                item_children_counter={"item1": 2})
        target = self._makeOne(order, candidate_id_list, mcounter_impl=mcounter_impl)
        
        #item.tokens, using_tokens
        with mock.patch("altair.app.ticketing.orders.enqueue.OrderedProductItemToken", new_callable=lambda : O, ):
            result = target.generate_tokens()
            self.assertEquals(len(item.tokens), 3)
            self.assertEquals(sum([len(vs) for vs in result.values()]), 2)

            ## generate token: seat3, seat1, seat2
            self.assertEqual(item.tokens[0].seat, seat3)
            self.assertEqual(item.tokens[1].seat, seat1)
            self.assertEqual(item.tokens[2].seat, seat2)
            self.assertEqual(item.tokens[0].item, item)
            self.assertEqual(item.tokens[1].item, item)
            self.assertEqual(item.tokens[2].item, item)

            ## enqueue candidates: seat1, seat2
            self.assertEqual(result[(unicode(item.id), unicode(seat1.id))], [item.tokens[1]])
            self.assertEqual(result[(unicode(item.id), unicode(seat2.id))], [item.tokens[2]])


    def test_generate_without_seat(self):
        candidate_id_list = [[None, "seat1", "item1", "ticket1"], [None, "seat2", "item1", "ticket1"]]
        item = OPI(id="item1", seats=[], tokens=[])
        order = Order(ordered_products=[])
        ordered_product = O(name="op", ordered_product_items=[], quantity=10)
        order.ordered_products.append(ordered_product)
        ordered_product.ordered_product_items.append(item)

        mcounter_impl = partial(FakeMaterialCounter, 
                                ordered_product_items=[item], 
                                tickets=[Ticket(id="ticket1")], 
                                item_children_counter={"item1": 2})
        target = self._makeOne(order, candidate_id_list, mcounter_impl=mcounter_impl)
        
        #item.tokens, using_tokens
        with mock.patch("altair.app.ticketing.orders.enqueue.OrderedProductItemToken", new_callable=lambda : O):
            result = target.generate_tokens()
            self.assertEquals(len(item.tokens), 10)
            self.assertEquals(sum([len(vs) for vs in result.values()]), 2)

            ## generated token: 
            self.assertEqual(item.tokens[0].seat, None)
            self.assertEqual(item.tokens[9].seat, None)
            self.assertEqual(item.tokens[0].item, item)
            self.assertEqual(item.tokens[9].item, item)

            ## enqueue candidates: 
            self.assertEqual(result[(unicode(item.id), unicode(None))], [item.tokens[0], item.tokens[1]])


    def test_without_seat(self):
        candidate_id_list = [[None, None, "item1", "ticket1"], [None, None, "item1", "ticket1"], [None, None, "item1", "ticket2"]]

        tokens = [Token(id=1), Token(id=2)]
        item = OPI(id="item1", seats=[], tokens=tokens)
        token_list_dict = {(unicode(item.id), unicode(None)): tokens}

        order = Order(ordered_products=[])
        mcounter_impl = partial(FakeMaterialCounter, 
                                ordered_product_items=[item], 
                                tickets=[Ticket(id="ticket1"), Ticket(id="ticket2")], 
                                item_children_counter={"item1": 2})
        target = self._makeOne(order, candidate_id_list, mcounter_impl=mcounter_impl, issuer="issuer")
        tickets_copy = target.mcounter.tickets[:]
        
        operator = Operator()
        with mock.patch("altair.app.ticketing.orders.enqueue.enqueue_token", autospec=True) as m:
            target._enqueue(operator, token_list_dict)
            m.assert_has_calls([mock.call(operator, tokens[0], tickets_copy[0], 1, 2, 
                                          **{"ordered_product_item":item, "order": order, "seat":None, "issuer":"issuer"}), 
                                mock.call(operator, tokens[1], tickets_copy[0], 2, 2, 
                                          **{"ordered_product_item":item, "order": order, "seat":None, "issuer":"issuer"}), 
                                mock.call(operator, tokens[0], tickets_copy[1], 3, 2,  #<- 3 is bug
                                          **{"ordered_product_item":item, "order": order, "seat":None, "issuer":"issuer"})])
            
    def test_with_seat(self):
        candidate_id_list = [[None, "seat1", "item1", "ticket1"], [None, "seat2", "item1", "ticket1"], [None, "seat2", "item1", "ticket2"]]

        tokens = [Token(id=1), Token(id=2)]
        item = OPI(id="item1", seats=[], tokens=tokens)
        token_list_dict = {(unicode(item.id), unicode("seat1")): [tokens[0]], 
                           (unicode(item.id), unicode("seat2")): [tokens[1]], 
                           }

        order = Order(ordered_products=[])
        mcounter_impl = partial(FakeMaterialCounter, 
                                ordered_product_items=[item], 
                                tickets=[Ticket(id="ticket1"), Ticket(id="ticket2")], 
                                seats=[Seat(id="seat1"), Seat(id="seat2")], 
                                item_children_counter={"item1": 2})
        target = self._makeOne(order, candidate_id_list, mcounter_impl=mcounter_impl, issuer="issuer")
        D = target.mcounter
        operator = Operator()
        with mock.patch("altair.app.ticketing.orders.enqueue.enqueue_token", autospec=True) as m:
            target._enqueue(operator, token_list_dict)
            m.assert_has_calls([mock.call(operator, tokens[0], D.tickets[0], 1, 2, 
                                          **{"ordered_product_item":item, "order": order, "seat":D.seats[0], "issuer":"issuer"}), 
                                mock.call(operator, tokens[1], D.tickets[0], 2, 2, 
                                          **{"ordered_product_item":item, "order": order, "seat":D.seats[1], "issuer":"issuer"}), 
                                mock.call(operator, tokens[1], D.tickets[1], 3, 2,  #<- 3 is bug
                                          **{"ordered_product_item":item, "order": order, "seat":D.seats[1], "issuer":"issuer"})])



if __name__  == "__main__":
    unittest.main()
