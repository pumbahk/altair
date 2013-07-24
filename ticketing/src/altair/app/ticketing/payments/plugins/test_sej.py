# -*- coding:utf-8 -*-

import unittest
from pyramid import testing

class FindApplicableTicketsTest(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from altair.app.ticketing.payments.plugins.sej import applicable_tickets_iter
        return applicable_tickets_iter(*args,  **kwargs)

    def test_it(self):
        from altair.app.ticketing.payments.plugins import SEJ_DELIVERY_PLUGIN_ID as DELIVERY_PLUGIN_ID
        class bundle(object):
            class sej_ticket:
                class ticket_format:
                    sej_delivery_method = testing.DummyResource(fee=0, delivery_plugin_id=DELIVERY_PLUGIN_ID)                    
                    delivery_methods = [sej_delivery_method]
            tickets = [sej_ticket]

        result = list(self._callFUT(bundle))
        self.assertEquals(len(result), 1)

    def test_with_another_ticket(self):
        from altair.app.ticketing.payments.plugins import SEJ_DELIVERY_PLUGIN_ID as DELIVERY_PLUGIN_ID
        class bundle(object):
            class sej_ticket:
                class ticket_format:
                    sej_delivery_method = testing.DummyResource(fee=0, delivery_plugin_id=DELIVERY_PLUGIN_ID)                    
                    delivery_methods = [sej_delivery_method]

            class another_ticket:
                class ticket_format:
                    another_delivery_method = testing.DummyResource(fee=0, delivery_plugin_id=-100)                    
                    delivery_methods = [another_delivery_method]
                    
            tickets = [sej_ticket, another_ticket, sej_ticket, another_ticket, sej_ticket]

        result = list(self._callFUT(bundle))
        self.assertEquals(len(result), 3)

        
if __name__ == "__main__":
    # setUpModule()
    unittest.main()
    


