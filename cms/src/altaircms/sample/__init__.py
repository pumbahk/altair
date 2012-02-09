def includeme(config):
    from . import core
    from . import api
    from . import widget
    core.includeme(config)
    api.includeme(config)
    widget.includeme(config)
    from pyramid.path import caller_package
    from pyramid.path import package_path


