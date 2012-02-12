def includeme(config):
    from . import core
    from . import api
    # from . import widget
    core.includeme(config)
    api.includeme(config)
    # widget.includeme(config)


