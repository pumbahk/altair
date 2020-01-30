import unittest
from .. import api

import logging
logger = logging.getLogger("ticket_hub")
logger.debug(__name__)

FACILITY_CODE = '00290'
AGENT_CODE = '9012'
ITEM_GROUP_CODE = '0001'
ITEM_CODE = '01001'

class TicketHubApiTest(unittest.TestCase):
    def setUp(self):
        self.api = api.TicketHubAPI(api.TicketHubClient(
            base_uri='https://stg.webket.jp/tickethub/v9',
            api_key='lQ1SDy',
            api_secret='Cpy*t^6^d}b',
            seller_code='06006',
            seller_channel_code='0011'
        ))

    @unittest.skip("External communication")
    def test_get_facility(self):
        res = self.api.facility(FACILITY_CODE)
        logger.info("facility res: %s" % vars(res))
        self.assertEqual(FACILITY_CODE, res.code)

    @unittest.skip("External communication")
    def test_get_item_groups(self):
        res = self.api.item_groups(FACILITY_CODE, AGENT_CODE)
        logger.info("item groups res: %s" % vars(res))
        self.assertEqual(FACILITY_CODE, res.facility_code)
        self.assertEqual(AGENT_CODE, res.agent_code)

    @unittest.skip("External communication")
    def test_get_items(self):
        res = self.api.items(FACILITY_CODE, AGENT_CODE, ITEM_GROUP_CODE)
        logger.info("items res: %s" % vars(res))
        self.assertEqual(FACILITY_CODE, res.facility_code)
        self.assertEqual(AGENT_CODE, res.agent_code)
        self.assertEqual(ITEM_GROUP_CODE, res.item_group_code)

    @unittest.skip("External communication")
    def test_create_cart(self):
        cart_items = [dict(item_group_code=ITEM_GROUP_CODE, items=[dict(item_code=ITEM_CODE, quantity=2)])]
        res = self.api.create_cart(FACILITY_CODE, AGENT_CODE, cart_items)
        logger.info("create cart res: %s" % vars(res))
        import time
        time.sleep(5)
        temp_order = self.api.create_temp_order(res.cart_id)
        logger.info("create temp order res: %s" % vars(temp_order))
        logger.info("created tickets: %s" % [vars(ticket) for ticket in temp_order.tickets])

    def test_complete_order(self):
        cart_items = [dict(item_group_code=ITEM_GROUP_CODE, items=[dict(item_code=ITEM_CODE, quantity=2)])]
        res = self.api.create_cart(FACILITY_CODE, AGENT_CODE, cart_items)
        #logger.info("create cart res: %s" % vars(res))
        import time
        time.sleep(5)
        temp_order = self.api.create_temp_order(res.cart_id)
        #logger.info("create temp order res: %s" % vars(temp_order))
        #logger.info("created tickets: %s" % [vars(ticket) for ticket in temp_order.tickets])
        completed = self.api.complete_order(temp_order.order_no)
        logger.info("completed order res: %s" % vars(completed))



