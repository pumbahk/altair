# coding: utf-8
from pyramid.exceptions import NotFound
from pyramid.renderers import render_to_response
from pyramid.view import view_config
from sqlalchemy.sql.expression import asc

from altaircms.models import DBSession, Page
from altaircms.widget.models import Page2Widget, Widget

@view_config(route_name='front')
def view(request):
    url = request.matchdict['page_name']

    dbsession = DBSession()

    page = dbsession.query(Page).filter_by(url=url).one()
    if not page:
        return NotFound()

    widgets = dbsession.query(Page2Widget, Widget).filter(Page2Widget.widget_id==Widget.id).\
        filter(Page2Widget.page_id==page.id).order_by(asc(Page2Widget.order)).all()

    tmpl = 'altaircms:templates/front/layout/' + str(page.layout_id) + '.mako'

    DBSession.remove()

    return render_to_response(
        tmpl, dict(
            page=page,
            widgets=widgets,
        ),
        request
    )
