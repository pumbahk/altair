def includeme(config):
    config.add_route("_jasmine", "_jasmine")
    config.add_view(jasmine_tests, route_name="_jasmine", renderer="ticketing.printqr:templates/_jasmine.html")

def jasmine_tests(context, request):
    return {}

