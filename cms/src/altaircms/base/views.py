# coding: utf-8
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.security import authenticated_userid, has_permission
from pyramid.view import view_config

from sqlalchemy.sql.expression import desc

from altaircms.fanstatic import bootstrap_need
from altaircms.models import DBSession, Event


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
