import functools
def includeme(config):
    add_route = functools.partial(config.add_route, factory=".resources.EventBoundTicketsResource")
    add_route("events.tickets.index", "event/{event_id}/")
    add_route("events.tickets.bind.ticket", "event/{event_id}/bind/ticket")
    add_route("events.tickets.api.ticketform", "/api/event/{event_id}/ticketform")
