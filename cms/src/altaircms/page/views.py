# coding: utf-8
import colander
import deform
import json

from pyramid.view import view_config
from pyramid.response import Response
from pyramid.exceptions import NotFound

import transaction

from altaircms.page.forms import PageMetadataEditForm, PageEditForm
from altaircms.models import DBSession, Page, Event
from altaircms.widget.models import Page2Widget


class PageEditView(object):
    def __init__(self, request):
        dbsession = DBSession()

        self.request = request
        self.page = None

        event_id = self.request.matchdict['event_id']
        if event_id:
            self.event = dbsession.query(Event).get(event_id)
            if not self.event:
                return NotFound()

            page_id = self.request.matchdict['page_id'] if 'page_id' in self.request.matchdict else None
            if page_id:
                self.page = dbsession.query(Page).filter_by(event_id=self.event.id, id=page_id).one()
                if not self.page:
                    return NotFound()

        DBSession.remove()

    def render_form(self, form, appstruct=colander.null, submitted='submit',
                    success=None, readonly=False):

        dbsession = DBSession()
        captured = None

        if submitted in self.request.POST:
            # the request represents a form submission
            try:
                # try to validate the submitted values
                controls = self.request.POST.items()
                captured = form.validate(controls)
                if success:
                    response = success(captured, self.event, self.page)
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
            'event':self.event,
            'page':self.page,
            'captured':repr(captured),
            'showmenu':True,
            'css_links':reqts['css'],
            'js_links':reqts['js'],
            }

    @view_config(route_name='page_add', renderer='altaircms:templates/page/form.mako')
    def page_add(self):
        """
        ページのメタデータ新規登録用ビュー
        """
        def succeed(captured, event=None, page=None):
            dbsession = DBSession()
            page = Page(
                event_id=event.id if event else None,
                url=captured['url'],
                title=captured['title'],
                description=captured['description'],
                keyword=captured['keyword'],
                # page.tags = captured['tags']
                )
            dbsession.add(page)

            transaction.commit()
            DBSession.remove()

            return Response('<div id="thanks">Thanks!</div>')

        DBSession.remove()
        return self.render_form(PageMetadataEditForm, success=succeed)

    @view_config(route_name='page_edit', renderer='altaircms:templates/page/edit.mako')
    def page_edit(self):
        """
        ページ内容の編集用ビュー
        """
        def succeed(captured, event=None, page=None):
            dbsession = DBSession()
            page_structure = json.loads(captured['structure'])

            for key, values in page_structure.iteritems():
                for value in values:
                    dbsession.add(
                        Page2Widget(
                            page_id=page.id,
                            widget_id=value,
                            block=key
                        )
                    )

            transaction.commit()
            DBSession.remove()

            return Response('<div id="thanks">Thanks!</div>')

        return self.render_form(PageEditForm, success=succeed)