def includeme(config):
    config.add_route('altair.app.ticketing.lots_admin.index', '/lots')
    config.add_route('altair.app.ticketing.lots_admin.search', '/lots/search')

    config.scan('.views')
