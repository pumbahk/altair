def includeme(config):
    #config.include(create_route)
    config.add_route("inquirypage", "/inquirypage")
    config.scan()

_created = False
def create_route(config):
    global _created
    if _created:
        return
    _created = True
    config.add_route("inquiry", "/inquiry")
