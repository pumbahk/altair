# coding: utf-8
import os
from datetime import date
from uuid import uuid4

import colander
import markupsafe
from deform.form import Form
from deform.exception import ValidationFailure

from pyramid.exceptions import NotFound
from pyramid.response import Response
from pyramid.view import view_config

from altaircms.asset import get_storepath
from altaircms.asset.models import Asset, ImageAsset
from altaircms.asset.forms import *
from altaircms.models import DBSession


class AssetEditView(object):
    def __init__(self, request):
        self.request = request
        self.asset_id = self.request.matchdict['asset_id'] if 'asset_id' in self.request.matchdict else None
        self.asset = DBSession.query(Asset).get(self.asset_id) if self.asset_id else None
        self.asset_type = self.request.matchdict['asset_type'] if 'asset_type' in self.request.matchdict else None

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
                appstruct = {'type': self.asset_type}
            html = markupsafe.Markup(form.render(appstruct))

        if self.request.is_xhr:
            return Response(html)

        reqts = form.get_widget_resources()

        # values passed to template for rendering
        return {
            'form':html,
            'captured':repr(captured),
            'asset_type': self.asset_type,
            }

    @view_config(route_name='asset_list', renderer='altaircms:templates/asset/list.mako', request_method='GET')
    def asset_list(self):
        assets = DBSession().query(Asset).all()

        return dict(
            assets=assets
        )

    @view_config(route_name="asset_form", renderer='altaircms:templates/asset/form.mako')
    def asset_form(self):
        def succeed(request, captured):
            # @TODO: モデルの追加処理を行う
            # @TODO: S3に対応する
            original_filename = captured['image']['filename']
            filename = '%s.%s' % (uuid4(), original_filename[original_filename.rfind('.') + 1:])
            today = date.today().strftime('%Y-%m-%d')

            storepath = os.path.join(get_storepath(request),  today)
            if not os.path.exists(storepath):
                os.makedirs(storepath)

            f = open(os.path.join(storepath, filename), 'wb')
            f.write(captured['image']['fp'].read())

            import pdb; pdb.set_trace()
            asset = ImageAsset(filepath=os.path.join(today, filename))
            DBSession.add(asset)

            return Response("hoge")

        if self.asset_type not in ASSET_TYPE:
            return NotFound()

        cls = globals()[self.asset_type.capitalize() + 'AssetSchema']()
        form = Form(cls, buttons=('submit', ), use_ajax=False)

        return self.render_form(form, success=succeed)

    @view_config(route_name="asset_edit")
    def asset_edit(self):
        pass

    @view_config(route_name="asset_delete")
    def asset_delete(self):
        pass

