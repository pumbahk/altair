import pkg_resources

def version(request):
    pkg = pkg_resources.get_distribution('altair.app.ticketing')
    return pkg.version

def includeme(config):
    config.set_request_property(version, 'version')
