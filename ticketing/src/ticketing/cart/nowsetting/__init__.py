def includeme(config):
    config.add_route("cart.nowsetting.form", "/form")
    config.add_route("cart.nowsetting.set", "/set")
    config.scan(".views")
