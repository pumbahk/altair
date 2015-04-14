def includeme(config):
    config.add_route('altair.app.ticketing.lots_admin.index', '/lots')
    config.add_route('altair.app.ticketing.lots_admin.search', '/lots/search')
    config.add_route('api.lots_admin.event.lot', '/lots/api')
    config.scan('.views')
