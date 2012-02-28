# coding: utf-8
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.security import authenticated_userid
from pyramid.view import view_config

from sqlalchemy.sql.expression import desc

from altaircms.fanstatic import bootstrap_need
from altaircms.models import DBSession
from altaircms.models import Event


@view_config(name='client', renderer='altaircms:templates/client/form.mako', permission='view')
def client(request):
    return dict()


@view_config(name='', renderer='altaircms:templates/dashboard.mako', permission='authenticated')
def dashboard(request):
    """
    ログイン後トップページ
    """
    bootstrap_need()

    events = DBSession.query(Event).order_by(desc(Event.event_open)).all()
    return dict(
        events=events
    )
