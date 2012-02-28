# coding: utf-8
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.security import authenticated_userid, has_permission
from pyramid.view import view_config

from sqlalchemy.sql.expression import desc

from altaircms.fanstatic import with_bootstrap
from altaircms.models import DBSession, Event


@view_config(name='', renderer='altaircms:templates/dashboard.mako', permission='authenticated')
@with_bootstrap
def dashboard(request):
    """
    ログイン後トップページ
    """
    events = DBSession.query(Event).order_by(desc(Event.event_open)).all()
    return dict(
        events=events
    )
