# coding: utf-8
from pyramid.httpexceptions import HTTPBadRequest, HTTPFound
from pyramid.view import view_config
from pyramid.view import view_defaults
from sqlalchemy.sql.expression import desc

from altaircms.lib.fanstatic_decorator import with_bootstrap
from altaircms.models import DBSession
from altaircms.event.models import Event
from altaircms.auth.models import APIKey
from altaircms.auth.forms import APIKeyForm


@view_config(renderer='altaircms:templates/dashboard.mako', permission='authenticated',
             decorator=with_bootstrap, route_name="dashboard")
def dashboard(request):
    """
    ログイン後トップページ
    """
    if request.user:
        events = request.allowable(Event).order_by(desc(Event.event_open)).limit(5)
    else:
        events = []
    return dict(
        events=events
    )

@view_defaults(decorator=with_bootstrap)
class APIKeyView(object):
    def __init__(self, request):
        self.request = request
        self.id = request.matchdict.get('id', None)
        #self.model_object = APIKeyAPI(self.request).read()
        self.model_object = DBSession.query(APIKey).filter_by(id=self.id).one() if self.id else None

    @view_config(route_name="apikey_list", request_method="POST", renderer="altaircms:templates/auth/apikey/list.mako")
    @view_config(route_name="apikey_list", request_method="GET", renderer="altaircms:templates/auth/apikey/list.mako")
    def read(self):
        if self.request.method == "POST":
            form = APIKeyForm(self.request.POST)
            if form.validate():
                DBSession.add(APIKey(name=form.data.get('name')))
                return HTTPFound(self.request.route_path("apikey_list"))
        else:
            form = APIKeyForm()

        return dict(
            form=form,
            apikeys=DBSession.query(APIKey)
        )

    @view_config(route_name="apikey", request_method="POST", request_param="_method=delete")
    def delete(self):
        if self.model_object:
            DBSession.delete(self.model_object)

        return HTTPFound(self.request.route_path("apikey_list"))

