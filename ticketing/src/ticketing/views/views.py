from pyramid.view import view_config


from ticketing.fanstatic import with_bootstrap
from ticketing.fanstatic import bootstrap_need


@view_config(route_name='index', renderer='ticketing:templates/index.html', permission='authenticated', decorator=with_bootstrap)
def index(context, request):
    return {}