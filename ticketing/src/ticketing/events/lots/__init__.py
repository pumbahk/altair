def includeme(config):
    config.add_route('lots.index', '/{event_id}')
    config.add_route('lots.new', '/new/{event_id}')
    config.add_route('lots.show', '/show/{lot_id}')
    config.add_route('lots.edit', '/edit/{lot_id}')

    config.add_route('lots.product_new', '/product_new/{lot_id}')
