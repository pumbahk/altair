# coding: utf-8
import inspect
import sys

import colander
import deform

from pyramid.response import Response
from pyramid.view import view_config
import transaction

from altaircms.page.forms import PageEditForm
from altaircms.models import DBSession, Page


class PageEditView(object):
    def __init__(self, request):
        self.request = request

    def render_form(self, form, appstruct=colander.null, submitted='submit',
                    success=None, readonly=False):

        captured = None

        if submitted in self.request.POST:
            # the request represents a form submission
            try:
                # try to validate the submitted values
                controls = self.request.POST.items()
                captured = form.validate(controls)
                if success:
                    response = success(captured)
                    if response is not None:
                        return response
                html = form.render(captured)
            except deform.ValidationFailure, e:
                # the submitted values could not be validated
                html = e.render()

        else:
            # the request requires a simple form rendering
            html = form.render(appstruct, readonly=readonly)

        if self.request.is_xhr:
            return Response(html)

        reqts = form.get_widget_resources()

        # values passed to template for rendering
        return {
            'form':html,
            'captured':repr(captured),
            'showmenu':True,
            'css_links':reqts['css'],
            'js_links':reqts['js'],
            }

    @view_config(route_name='page_add', renderer='altaircms:templates/page/form.mako')
    def edit(self):
        def succeed(captured):
            dbsession = DBSession()

            page = Page(
                url=captured['url'],
                title=captured['title'],
                description=captured['description'],
                keyword=captured['keyword'],
                # page.tags = appstruct['tags']
                )

            dbsession.add(page)
            transaction.commit()

            DBSession.remove()

            return Response('<div id="thanks">Thanks!</div>')
        return self.render_form(PageEditForm, success=succeed)
