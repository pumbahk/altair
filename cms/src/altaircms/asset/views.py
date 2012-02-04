# coding: utf-8
import colander
import deform
from pyramid.exceptions import NotFound
from pyramid.response import Response
from pyramid.view import view_config

from altaircms.asset.models import Asset
from altaircms.asset.forms import *
from altaircms.models import DBSession


class AssetEditView(object):
    def __init__(self, request):
        self.request = request
        self.asset_id = self.request.matchdict['asset_id'] if 'asset_id' in self.request.matchdict else None
        self.asset_type = self.request.matchdict['asset_type'] if 'asset_type' in self.request.matchdict else None

        if self.asset_id:
            self.asset = DBSession.query(Asset).get(self.asset_id)

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
#            'showmenu':True,
#            'css_links':reqts['css'],
#            'js_links':reqts['js'],
            }
    """
    @view_config(route_name='page_add', renderer='altaircms:templates/page/form.mako')
    def page_add(self):
        """
        ## ページのメタデータ新規登録用ビュー
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
            dbsession.save(page)

            transaction.commit()
            DBSession.remove()

            return Response('<div id="thanks">Thanks!</div>')

        DBSession.remove()
        return self.render_form(PageMetadataEditForm, success=succeed)

    @view_config(route_name='page_edit', renderer='altaircms:templates/page/edit.mako')
    def page_edit(self):
        """
        ## ページ内容の編集用ビュー
    """
        def succeed(captured, event=None, page=None):
            dbsession = DBSession()

            self.page.layout_id = captured['layout_id']
            dbsession.add(self.page)

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

        for key, values in self.display_blocks.iteritems():
            self.display_blocks[key] = [value.id for value in values]

        appstruct = {
            'layout_id': self.page.layout_id if self.page.layout_id else 0,
            'structure': json.dumps(self.display_blocks)
        }

        return self.render_form(PageEditForm, appstruct=appstruct, success=succeed)
    """


    @view_config(route_name="asset_add")
    def asset_add(self):
        pass

    @view_config(route_name="asset_edit")
    def asset_edit(self):
        pass

    @view_config(route_name="asset_form", renderer='altaircms:templates/asset/form.mako')
    def asset_form(self):
        if self.asset_type not in ASSET_TYPE:
            return NotFound()

        cls = globals()[self.asset_type.capitalize() + 'AssetForm']

        return self.render_form(cls)

    @view_config(route_name="asset_delete")
    def asset_delete(self):
        pass

    @view_config(route_name='asset_list', renderer='altaircms:templates/asset/list.mako')
    def asset_list(self):
        assets = DBSession().query(Asset).all()

        return dict(
            assets=assets
        )
