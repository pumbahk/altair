def includeme(config):
    config.add_route('cart.index', 'events/{event_id}')
    config.add_subscriber('.subscribers.add_helpers', 'pyramid.events.BeforeRender')
    config.add_route('cart.seat_types', 'events/{event_id}/performances/{performance_id}/seat_types')
