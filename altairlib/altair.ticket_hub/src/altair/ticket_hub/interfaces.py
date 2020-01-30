from zope.interface import Interface

class ITicketHubAPI(Interface):
    def healths(self):
        pass
    def facility(self, id):
        pass
    def item_groups(self, facility_code, agent_code):
        pass
    def items(self, facility_code, agent_code, item_group_code):
        pass
    def create_cart(self, facility_code, agent_code, item_group_code, item_code, item_quantity):
        pass
    def create_temp_order(self, tickethub_cart_id):
        pass
    def complete_order(self, tickethub_order_no):
        pass