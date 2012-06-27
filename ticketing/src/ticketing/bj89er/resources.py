from ticketing.cart.resources import TicketingCartResrouce

class Bj89erCartResource(TicketingCartResrouce):
    def __init__(self, request):
        super(Bj89erCartResource, self).__init__(request)
        self.event_id = request.registry.settings['89er.event_id']
        self.performance_id = request.registry.settings['89er.performance_id']
