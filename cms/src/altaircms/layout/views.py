# coding: utf-8
from deform.exception import ValidationFailure
from deform.form import Form
from markupsafe import Markup
from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.sql.expression import desc

from altaircms.models import DBSession
from altaircms.layout.models import Layout
from altaircms.layout.forms import LayoutSchema


@view_config(route_name='layout_list', renderer='altaircms:templates/layout/list.mako')
def list(request):
    form = Form(LayoutSchema(), buttons=('submit', ))

    if 'submit' in request.POST:
        try:
            controls = request.POST.items()
            captured = form.validate(controls)
            # html = form.render(captured)

            layout = Layout(
                title=captured['title'],
                template_filename=captured['template_filename']
            )
            DBSession.add(layout)

            html = Markup("<p>Thanks!</p>")
        except ValidationFailure, e:
            html = Markup(e.render())

        if request.is_xhr:
            return Response(Markup(html))
    else:
        html = Markup(form.render())

    return dict(
        layouts=DBSession.query(Layout).order_by(desc(Layout.id)).all(),
        form=html,
    )


@view_config(route_name='layout', renderer='altaircms:templates/layout/view.mako')
def view(request):
    id_ = request.matchdict.get('layout_id')
    layout = DBSession.query(Layout).get(id_)
    return dict(
        layout=layout
    )
