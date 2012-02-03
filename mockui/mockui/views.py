from pyramid.view import view_config
from mockui.fanstatic import jqueries_need

@view_config(route_name="home", renderer="index.mak")
def my_view(request):
    jqueries_need()
    return {'project':'mockui'}

## api sample view

