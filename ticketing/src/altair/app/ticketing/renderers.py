def status_handler(request, value):
    status = value.pop('_status', None)
    if status is None:
        if value.get('success', True):
            status = 200
        else:
            status = 401
    return int(status)

def includeme(config):
    from altair.pyramid_extra_renderers.json import JSON
    from altair.pyramid_extra_renderers.csv import CSV
    from altair.pyramid_extra_renderers.xml import XML
    config.add_renderer('json'  , JSON(status_handler=status_handler))
    config.add_renderer('csv'   , CSV(default_encoding='CP932'))
    config.add_renderer('lxml'  , XML())
