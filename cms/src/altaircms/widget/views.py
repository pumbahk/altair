# coding: utf-8
import json
import os

import colander
import markupsafe
from deform.form import Form
from deform.exception import ValidationFailure

from pyramid.exceptions import NotFound
from pyramid.response import Response
from pyramid.view import view_config
from sqlalchemy.sql.expression import desc

from altaircms.models import DBSession
from altaircms.widget.forms import *
from altaircms.widget.models import *
from altaircms.asset import get_storepath


class WidgetEditView(object):
    def __init__(self, request):
        self.request = request
        self.widget_id = self.request.matchdict['widget_id'] if 'widget_id' in self.request.matchdict else None
        self.widget = DBSession.query(Widget).get(self.widget_id) if self.widget_id else None
        self.widget_type = self.request.matchdict['widget_type'] if 'widget_type' in self.request.matchdict else None

    def response_json_ok(self):
        # @TODO: 他のAPI呼び出しなどと共通化する
        content = json.dumps(dict(status='OK'))
        content_type = 'application/json'
        return Response(content, content_type=content_type)

    def render_form(self, form, appstruct=colander.null, submitted='submit',
                    success=None, readonly=False):
        captured = None

        if submitted in self.request.POST:
            try:
                controls = self.request.POST.items()
                captured = form.validate(controls)
                if success:
                    response = success(self.request, captured)
                    if response is not None:
                        return response
                html = markupsafe.Markup(form.render(captured))
            except ValidationFailure, e:
                html = markupsafe.Markup(e.render())

        else:
            if not appstruct:
                appstruct = {'type': self.widget_type}
            html = markupsafe.Markup(form.render(appstruct))

        if self.request.is_xhr:
            return Response(html)

        reqts = form.get_widget_resources()

        # values passed to template for rendering
        return {
            'form':html,
            'captured':repr(captured),
            'widget_type': self.widget_type,
            }

    @view_config(route_name='widget_list', renderer='altaircms:templates/widget/list.mako', request_method='GET', permission='edit')
    def widget_list(self):
        widgets = DBSession().query(Widget).order_by(desc(Widget.id)).all()

        return dict(
            widgets=widgets
        )

    @view_config(route_name='widget_add', permission='edit', renderer='altaircms:templates/widget/form.mako')
    def widget_form(self):
        def succeed(request, captured):
            mdl = globals()[self.widget_type.capitalize() + 'Widget']
            obj = mdl(captured)
            DBSession.add(obj)

            return Response('<p>Thanks!</p>')

        cls = globals()[self.widget_type.capitalize() + 'WidgetSchema']()
        form = Form(cls, buttons=('submit',), use_ajax=True)
        return self.render_form(form, success=succeed)

    @view_config(route_name="widget", permission='edit', renderer='altaircms:templates/widget/view.mako', request_method='GET')
    def widget_edit(self):
        return dict(
            widget=self.widget
        )

    @view_config(route_name="widget", permission='edit', request_method='POST')
    def widget_delete(self):
        if not self.widget:
            return NotFound()

        if '_method' in self.request.params and self.request.params['_method'].lower() == 'delete':
            # 削除処理
            if hasattr(self.widget, 'filepath'):
                os.remove(os.path.join(get_storepath(self.request), self.widget.filepath))
            DBSession.delete(self.widget)

            return self.response_json_ok()
        else:
            # 更新処理
            pass
