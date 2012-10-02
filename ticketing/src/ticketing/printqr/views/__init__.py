def includeme(config):
    config.add_route("index", "/")
    config.add_route("api.ticket.data", "/api/ticket/data")
    config.add_route('api.applet.formats', '/api/applet/formats')
    config.add_route('api.applet.enqueue', '/api/applet/enqueue')
    config.add_route('api.applet.peek', '/api/applet/peek')
    config.add_route('api.applet.dequeue', '/api/applet/dequeue')
    config.scan(".app")
    
    config.add_route("login", "/login")
    config.add_route("logout", "/logout")
    config.scan(".login")
