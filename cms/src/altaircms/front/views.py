# coding: utf-8
from pyramid.exceptions import NotFound
from pyramid.renderers import render_to_response
from pyramid.view import view_config
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import asc

from altaircms.models import DBSession, Page, Layout
from altaircms.widget.models import Page2Widget, Widget


@view_config(route_name='front')
def view(request):
    url = request.matchdict['page_name']

    dbsession = DBSession()

    try:
        (page, layout) = dbsession.query(Page, Layout).filter(Page.layout_id==Layout.id).filter_by(url=url).one()
    except NoResultFound:
        return NotFound(u'レイアウトが設定されていません。')

    results = dbsession.query(Page2Widget, Widget).filter(Page2Widget.widget_id==Widget.id).\
        filter(Page2Widget.page_id==page.id).order_by(asc(Page2Widget.order)).all()

    DBSession.remove()

    import pdb; pdb.set_trace()

    # ウィジェットの組み立て
    display_blocks = {}
    for p2w, widget in results:
        key = p2w.block
        if key in display_blocks:
            display_blocks[key].append(widget)
        else:
            display_blocks[key] = [widget]

    tmpl = 'altaircms:templates/front/layout/' + str(layout.template_filename)

    return render_to_response(
        tmpl, dict(
            page=page,
            display_blocks=display_blocks
        ),
        request
    )
