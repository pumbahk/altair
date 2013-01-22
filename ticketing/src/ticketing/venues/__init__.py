def includeme(config):
    config.add_route("venues.index", "/")
    config.add_route("venues.show", "/show/{venue_id}")
    config.add_route("venues.checker", "/{venue_id}/checker")
    config.add_route("api.get_drawing", "/{venue_id}/get_drawing")
    config.add_route("api.get_seats", "/{venue_id}/seats/")
    config.add_route("api.get_frontend", "/{venue_id}/frontend/{part}")
    config.add_route("seats.download", "/download/{venue_id}")
    config.scan(".")
