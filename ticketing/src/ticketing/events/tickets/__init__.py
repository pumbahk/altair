import functools
def includeme(config):
    add_route = functools.partial(config.add_route, factory=".resources.EventBoundTicketsResource")
    add_route("events.tickets.index", "/event/{event_id}/")
    add_route("events.tickets.bind.ticket", "/event/{event_id}/bind/ticket")

    add_route("events.tickets.bundles.new", "/event/{event_id}/bundle/new")
    add_route("events.tickets.bundles.edit", "/event/{event_id}/bundle/{bundle_id}/edit")
    add_route("events.tickets.bundles.delete", "/event/{event_id}/bundle/{bundle_id}/delete")
    add_route("events.tickets.bundles.show", "/event/{event_id}/bundle/{bundle_id}")

    add_route("events.tickets.attributes.new", "/event/{event_id}/bundle/{bundle_id}/attribute/new")
    add_route("events.tickets.attributes.edit", "/event/{event_id}/bundle/{bundle_id}/attribute/{attribute_id}/edit")

    add_route("events.tickets.api.ticketform", "/api/event/{event_id}/_ticketform")
    add_route("events.tickets.api.bundleform", "/api/event/{event_id}/_bundleform")

    config.scan(".views")
