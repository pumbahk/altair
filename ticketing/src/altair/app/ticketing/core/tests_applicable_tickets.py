# -*- encoding:utf-8 -*-
import unittest
from pyramid import testing
from datetime import datetime

def setUpModule():
    from altair.app.ticketing.testing import _setup_db
    _setup_db(modules=[
            "altair.app.ticketing.models",
            "altair.app.ticketing.core.models",
            "altair.app.ticketing.cart.models",
            ])

def tearDownModule():
    from altair.app.ticketing.testing import _teardown_db
    _teardown_db()

class IssuedPrintedSetterTests(unittest.TestCase):
    def tearDown(self):
        import transaction
        transaction.abort()

    def _getTarget(self):
        from altair.app.ticketing.core.utils import ApplicableTicketsProducer
        return ApplicableTicketsProducer

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args,**kwargs)

    def test_sej_only_with_other(self):
        """ SEJの券面だけを取り出す"""
        from altair.app.ticketing.models import DBSession
        from altair.app.ticketing.payments.plugins.sej import DELIVERY_PLUGIN_ID as DELIVERY_PLUGIN_ID_SEJ
        from altair.app.ticketing.core.models import TicketBundle, Ticket, TicketFormat, DeliveryMethod

        sej_ticket_fmt = TicketFormat(name="", )
        sej_ticket_fmt.delivery_methods.append(DeliveryMethod(fee=0, delivery_plugin_id=DELIVERY_PLUGIN_ID_SEJ))

        other_ticket_fmt1 = TicketFormat(name="", )
        other_ticket_fmt1.delivery_methods.append(DeliveryMethod(fee=0, delivery_plugin_id=-1))
        other_ticket_fmt2 = TicketFormat(name="", )
        other_ticket_fmt2.delivery_methods.append(DeliveryMethod(fee=0, delivery_plugin_id=-2))

        bundle = TicketBundle()
        bundle.tickets.append(Ticket(ticket_format=sej_ticket_fmt))
        bundle.tickets.append(Ticket(ticket_format=other_ticket_fmt1))
        bundle.tickets.append(Ticket(ticket_format=other_ticket_fmt2))

        DBSession.add(bundle)

        target = self._makeOne(bundle=bundle)
        result = list(target.sej_only_tickets())

        self.assertEquals(len(result),  1)
        
    def test_sej_only_with_format_id(self):
        """(format_idが渡された場合) SEJ券面を探し かつ 指定されたformat_idと等しいものだけを取り出す"""
        from altair.app.ticketing.models import DBSession
        from altair.app.ticketing.payments.plugins.sej import DELIVERY_PLUGIN_ID as DELIVERY_PLUGIN_ID_SEJ
        from altair.app.ticketing.core.models import TicketBundle, Ticket, TicketFormat, DeliveryMethod

        sej_ticket_fmt1 = TicketFormat(name="", )
        sej_ticket_fmt1.delivery_methods.append(DeliveryMethod(fee=0, delivery_plugin_id=DELIVERY_PLUGIN_ID_SEJ))

        sej_ticket_fmt2 = TicketFormat(name="", )
        sej_ticket_fmt2.delivery_methods.append(DeliveryMethod(fee=0, delivery_plugin_id=DELIVERY_PLUGIN_ID_SEJ))

        other_ticket_fmt = TicketFormat(name="", )
        other_ticket_fmt.delivery_methods.append(DeliveryMethod(fee=0, delivery_plugin_id=-1))

        bundle = TicketBundle()
        bundle.tickets.append(Ticket(ticket_format=sej_ticket_fmt1))
        bundle.tickets.append(Ticket(ticket_format=sej_ticket_fmt2))
        bundle.tickets.append(Ticket(ticket_format=other_ticket_fmt))

        DBSession.add(bundle)
        DBSession.flush()

        target = self._makeOne(bundle=bundle)
        self.assertEquals(len(list(target.sej_only_tickets())), 2)
        self.assertEquals(len(list(target.sej_only_tickets(sej_ticket_fmt1.id))), 1)


    def test_will_issued_by_own(self):
        """自社発券用の券面を取り出す。"""
        from altair.app.ticketing.models import DBSession
        from altair.app.ticketing.payments.plugins.sej import DELIVERY_PLUGIN_ID as DELIVERY_PLUGIN_ID_SEJ
        from altair.app.ticketing.core.models import TicketBundle, Ticket, TicketFormat, DeliveryMethod

        sej_ticket_fmt1 = TicketFormat(name="", )
        sej_ticket_fmt1.delivery_methods.append(DeliveryMethod(fee=0, delivery_plugin_id=DELIVERY_PLUGIN_ID_SEJ))

        sej_ticket_fmt2 = TicketFormat(name="", )
        sej_ticket_fmt2.delivery_methods.append(DeliveryMethod(fee=0, delivery_plugin_id=DELIVERY_PLUGIN_ID_SEJ))

        other_ticket_fmt = TicketFormat(name="", )
        other_ticket_fmt.delivery_methods.append(DeliveryMethod(fee=0, delivery_plugin_id=-1))

        bundle = TicketBundle()
        bundle.tickets.append(Ticket(ticket_format=sej_ticket_fmt1))
        bundle.tickets.append(Ticket(ticket_format=sej_ticket_fmt2))
        bundle.tickets.append(Ticket(ticket_format=other_ticket_fmt))

        DBSession.add(bundle)
        DBSession.flush()

        target = self._makeOne(bundle=bundle)
        result = list(target.will_issued_by_own_tickets())
        self.assertEquals(len(result),  1)

    def test_will_issued_by_own2(self):
        """自社発券用の券面を取り出す。"""
        from altair.app.ticketing.models import DBSession
        from altair.app.ticketing.payments.plugins.sej import DELIVERY_PLUGIN_ID as DELIVERY_PLUGIN_ID_SEJ
        from altair.app.ticketing.core.models import TicketBundle, Ticket, TicketFormat, DeliveryMethod

        sej_ticket_fmt1 = TicketFormat(name="", )
        sej_ticket_fmt1.delivery_methods.append(DeliveryMethod(fee=0, delivery_plugin_id=DELIVERY_PLUGIN_ID_SEJ))
        sej_ticket_fmt1.delivery_methods.append(DeliveryMethod(fee=0, delivery_plugin_id=-1))

        bundle = TicketBundle()
        bundle.tickets.append(Ticket(ticket_format=sej_ticket_fmt1))

        DBSession.add(bundle)
        DBSession.flush()

        target = self._makeOne(bundle=bundle)
        result = list(target.will_issued_by_own_tickets())
        self.assertEquals(len(result),  0)


if __name__ == "__main__":
    unittest.main()
