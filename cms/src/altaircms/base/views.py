# coding: utf-8
from pyramid.httpexceptions import HTTPBadRequest, HTTPFound
from pyramid.security import authenticated_userid, has_permission
from pyramid.view import view_config

from sqlalchemy.sql.expression import desc
import transaction

from altaircms.fanstatic import with_bootstrap, bootstrap_need
from altaircms.models import DBSession, Event
from altaircms.auth.models import APIKey
from altaircms.views import BaseRESTAPI
from altaircms.auth.forms import APIKeyForm


@view_config(name='', renderer='altaircms:templates/dashboard.mako', permission='authenticated', 
             decorator=with_bootstrap)
def dashboard(request):
    """
    ログイン後トップページ
    """
    events = DBSession.query(Event).order_by(desc(Event.event_open)).all()
    return dict(
        events=events
    )


class APIKeyView(object):
    def __init__(self, request):
        self.request = request
        self.id = request.matchdict.get('id', None)
        #self.model_object = APIKeyAPI(self.request).read()
        self.model_object = DBSession.query(APIKey).filter_by(id=self.id).one() if self.id else None

        bootstrap_need()

    @view_config(route_name="apikey_list", request_method="POST", renderer="altaircms:templates/auth/apikey/list.mako")
    @view_config(route_name="apikey_list", request_method="GET", renderer="altaircms:templates/auth/apikey/list.mako")
    def read(self):
        if self.request.method == "POST":
            form = APIKeyForm(self.request.POST)
            if form.validate():
                DBSession.add(APIKey(name=form.data.get('name')))
                return HTTPFound(self.request.route_url("apikey_list"))
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

        return HTTPFound(self.request.route_url("apikey_list"))


class APIKeyAPI(BaseRESTAPI):
    model = APIKey
