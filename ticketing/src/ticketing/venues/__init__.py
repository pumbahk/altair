def includeme(config):
    config.add_route("api.get_drawing", "/{venue_id}/get_drawing")
    config.add_route("api.get_seats", "/{venue_id}/seats/")
