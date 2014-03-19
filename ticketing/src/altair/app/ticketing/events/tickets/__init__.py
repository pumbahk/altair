import functools
def includeme(config):
    add_route = functools.partial(config.add_route, factory=".resources.EventBoundTicketsResource")
    add_route("events.tickets.index", "/event/{event_id}/")
    add_route("events.tickets.bind.ticket", "/event/{event_id}/bind/ticket")

    add_route('events.tickets.boundtickets.show', '/event/{event_id}/ticket/{id}')
    add_route('events.tickets.boundtickets.edit', '/event/{event_id}/ticket/{id}/edit')
    add_route('events.tickets.boundtickets.download', '/event/{event_id}/ticket/{id}/download')
    add_route('events.tickets.boundtickets.delete', '/event/{event_id}/ticket/{id}/delete')
    add_route('events.tickets.boundtickets.data', '/event/{event_id}/ticket/{id}/data')

    add_route("events.tickets.bundles.new", "/event/{event_id}/bundle/new")
    add_route("events.tickets.bundles.edit", "/event/{event_id}/bundle/{bundle_id}/edit")
    add_route("events.tickets.bundles.delete", "/event/{event_id}/bundle/{bundle_id}/delete")
    add_route("events.tickets.bundles.show", "/event/{event_id}/bundle/{bundle_id}")

    add_route("events.tickets.attributes.new", "/event/{event_id}/bundle/{bundle_id}/attribute/new")
    add_route("events.tickets.attributes.edit", "/event/{event_id}/bundle/{bundle_id}/attribute/{attribute_id}/edit")
    add_route("events.tickets.attributes.delete", "/event/{event_id}/bundle/{bundle_id}/attribute/{attribute_id}/delete")

    add_route("events.tickets.api.ticketform", "/api/event/{event_id}/_ticketform")
    add_route("events.tickets.api.bundleform", "/api/event/{event_id}/_bundleform")
    
    config.add_view("altair.app.ticketing.tickets.views.TicketTemplates",
                    attr="edit", request_method="GET", 
                    route_name="events.tickets.boundtickets.edit", 
                    renderer='altair.app.ticketing:templates/tickets/events/tickets/new.html')
    config.add_view("altair.app.ticketing.tickets.views.TicketTemplates",
                    attr="edit_post", request_method="POST", 
                    route_name="events.tickets.boundtickets.edit", 
                    renderer='altair.app.ticketing:templates/tickets/events/tickets/new.html')
    config.add_view("altair.app.ticketing.tickets.views.TicketTemplates",
                    attr="delete", request_method="GET", 
                    route_name="events.tickets.boundtickets.delete", 
                    renderer='altair.app.ticketing:templates/tickets/events/_deleteform.html')
    config.add_view("altair.app.ticketing.tickets.views.TicketTemplates",
                    attr="delete_post", request_method="POST", 
                    route_name="events.tickets.boundtickets.delete")
    config.add_view("altair.app.ticketing.tickets.views.TicketTemplates",
                    attr="show", request_method="GET", 
                    route_name="events.tickets.boundtickets.show", 
                    renderer='altair.app.ticketing:templates/tickets/events/tickets/show.html')
    config.add_view("altair.app.ticketing.tickets.views.TicketTemplates",
                    attr="download", request_method="GET", 
                    route_name="events.tickets.boundtickets.download")
    config.add_view("altair.app.ticketing.tickets.views.TicketTemplates",
                    attr="data", request_method="GET", 
                    route_name="events.tickets.boundtickets.data", 
                    renderer="json")
    config.scan(".views")
