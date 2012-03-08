# coding: utf-8
import colander
import deform
import json
import transaction
import sqlalchemy.orm as orm

from pyramid.view import view_config
from pyramid.response import Response
from pyramid.exceptions import NotFound
from pyramid.httpexceptions import HTTPFound

from altaircms.views import BaseRESTAPI
from altaircms.page.forms import PageForm
from altaircms.models import DBSession, Event
from altaircms.page.models import Page

from altaircms.page.mappers import PageMapper, PagesMapper
from altaircms.layout.models import Layout

from altaircms.fanstatic import with_bootstrap
from altaircms.fanstatic import with_fanstatic_jqueries
from altaircms.fanstatic import with_wysiwyg_editor


"""
@view_config(route_name='page_object', renderer='altaircms:templates/page/edit.mako', permission='view')
def view(request):
    id_ = request.matchdict['id']

    page = PageRESTAPIView(request, id_).read()
    ## layout render
    layout_render = request.context.get_layout_render(page)
    page_render = request.context.get_page_render(page)
    ## fanstatic

    from altaircms.fanstatic import jqueries_need
    from altaircms.fanstatic import wysiwyg_editor_need
    jqueries_need()
    wysiwyg_editor_need()

    return dict(
        pages=page,
        layout_render=layout_render,
        page_render=page_render,
    )
"""

@view_config(route_name='page', renderer='altaircms:templates/page/list.mako', permission='page_create', request_method="POST", 
             decorator=with_bootstrap)
@view_config(route_name='page', renderer='altaircms:templates/page/list.mako', permission='page_read', request_method="GET", 
             decorator=with_bootstrap)
def list_(request):
    layout_choices = [(layout.id, layout.title) for layout in DBSession.query(Layout)]
    if request.method == "POST":
        form = PageForm(request.POST)
        form.layout_id.choices = layout_choices
        if form.validate():
            request.method = "PUT"
            PageRESTAPIView(request).create()
            return HTTPFound(request.route_url("page"))
    else:
        form = PageForm()
        form.layout_id.choices = layout_choices

    return dict(
        pages=PageRESTAPIView(request).read(),
        form=form
    )


class PageRESTAPIView(BaseRESTAPI):
    model = Page
    form = PageForm
    object_mapper = PageMapper
    objects_mapper = PagesMapper

    def _post_form_hook(self):
        layout_choices = [(layout.id, layout.title) for layout in DBSession.query(Layout)]
        self.form_object.layout_id.choices = layout_choices

@view_config(route_name="page_edit_", request_method="POST")
def to_publish(request):     ## fixme
    page_id = request.matchdict["page_id"]
    page = Page.query.filter(Page.id==page_id).one()
    page.to_published()
    return HTTPFound(request.route_url("page_edit_", page_id=page_id))


class PageEditView(object):
    def __init__(self, request):
        self.request = request
        self.page = None
        self.event = None

        event_id = self.request.matchdict.get('event_id', None)
        if event_id:
            self.event = DBSession.query(Event).get(event_id)
            if not self.event:
                return NotFound()

        page_id = self.request.matchdict.get('page_id', None)
        if page_id:
            qs = DBSession.query(Page)
            if event_id:
                self.page = qs.filter_by(event_id=self.event.id, id=page_id).one()
            else:
                self.page = qs.filter_by(id=page_id).one()

            if not self.page:
                return NotFound()
            '''
            results = dbsession.query(Page2Widget, Widget).filter(Page2Widget.widget_id==Widget.id).\
                filter(Page2Widget.page_id==page_id).order_by(asc(Page2Widget.order)).all()

            self.display_blocks = {}
            for p2w, widget in results:
                key = p2w.block
                if key in self.display_blocks:
                    self.display_blocks[key].append(widget)
                else:
                    self.display_blocks[key] = [widget]
            '''
            self.display_blocks = {}

    def render_form(self, form, appstruct=colander.null, submitted='submit', duplicated='duplicate',
                    success=None, readonly=False, extra_context=None):
        captured = None

        if submitted in self.request.POST or duplicated in self.request.POST:
            # the request represents a form submission
            try:
                # try to validate the submitted values
                controls = self.request.POST.items()
                captured = form.validate(controls)
                if success:
                    duplicate = True if duplicated in self.request.POST else False
                    response = success(captured, duplicate=duplicate)
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


        ctx =  {
            'form':html,
            'event':self.event,
            'page':self.page,
            'pages':DBSession.query(Page).all(),
            'captured':repr(captured),
            'showmenu':True,
            'css_links':reqts['css'],
            'js_links':reqts['js'],
        }
        
        if extra_context:
            ctx.update(extra_context)

        # values passed to template for rendering
        return ctx

    @view_config(route_name='page_add', renderer='altaircms:templates/page/edit.mako')
    def page_add(self):
        appstruct = {
            'layout_id': 1,
            'structure': '{}',
        }

        return self.render_form(PageAddForm, success=self._succeed, appstruct=appstruct)

    @view_config(route_name='page_edit_', renderer='altaircms:templates/page/edit.mako', permission='authenticated', 
                 decorator=with_fanstatic_jqueries.merge(with_bootstrap).merge(with_wysiwyg_editor))
    @view_config(route_name='page_edit', renderer='altaircms:templates/page/edit.mako', permission='authenticated', 
                 decorator=with_fanstatic_jqueries.merge(with_bootstrap).merge(with_wysiwyg_editor))
    def page_edit(self):
        if not self.page:
            return self.render_form(PageEditForm, appstruct={}, success=self._succeed)            
        else:
            # @TODO: モデルプロパティとして移したほうがいいかも知れない
            for key, values in self.display_blocks.iteritems():
                self.display_blocks[key] = [value.id for value in values]

            appstruct = {
                'url': self.page.url,
                'title': self.page.title,
                'description': self.page.description,
                'keywords': self.page.keywords,
                'layout_id': self.page.layout_id if self.page.layout_id else 0,
                'structure': json.dumps(self.display_blocks)
            }

            ## layout render
            layout_render = self.request.context.get_layout_render(self.page)
            page_render = self.request.context.get_page_render(self.page)

            '''
            return self.render_form(PageEditForm, appstruct=appstruct, success=self._succeed,
                                    extra_context={"layout_render": layout_render,
                                                   "page_render": page_render})
            '''
            return {
                'form':'',
                'page':self.page,
                "layout_render": layout_render,
                "page_render": page_render
            }



    def _succeed(self, captured, duplicate=False):
        dbsession = DBSession()

        if duplicate or not self.page:
            page = Page(
                event_id=self.event.id if self.event else None,
                url=captured['url'],
                title=captured['title'],
                description=captured['description'],
                keywords=captured['keywords'],
                layout_id=captured['layout_id'],
                # page.tags = captured['tags']
            )
        else:
            self.page.url = captured['url']
            self.page.title = captured['title']
            self.page.description = captured['description']
            self.page.keywords = captured['keywords']
            self.page.layout_id = captured['layout_id']

            page = self.page

        dbsession.add(page)

        # page_structure = json.loads(captured['structure'])

        # q = dbsession.query(Page2Widget).filter_by(page_id=page.id)
        # for p2w in q:
        #     dbsession.delete(p2w)

        # for key, values in page_structure.iteritems():
        #     for value in values:
        #         dbsession.add(
        #             Page2Widget(
        #                 page_id=page.id,
        #                 widget_id=value,
        #                 block=key
        #             )
        #         )

        transaction.commit()
        DBSession.remove()

        return Response('<div id="thanks">Thanks!</div>')
