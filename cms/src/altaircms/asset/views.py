# coding: utf-8
import json
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
from sqlalchemy.sql.expression import desc

from altaircms.asset import get_storepath
from altaircms.asset.models import Asset, ImageAsset, MovieAsset, FlashAsset
from altaircms.asset.forms import *
from altaircms.models import DBSession


EXT_MAP = {
    'jpg':'image/jpeg',
    'png':'image/png',
    'gif':'image/gif',
    'mov':'video/quicktime',
    'mp4':'video/quicktime',
    'swf':'application/x-shockwave-flash',
}

def detect_mimetype(filename):
    ext = filename[filename.rfind('.') + 1:].lower()

    if ext in EXT_MAP:
        return EXT_MAP[ext]
    else:
        return 'application/octet-stream'


class AssetEditView(object):
    def __init__(self, request):
        self.request = request
        self.asset_id = self.request.matchdict['asset_id'] if 'asset_id' in self.request.matchdict else None
        self.asset = DBSession.query(Asset).get(self.asset_id) if self.asset_id else None
        self.asset_type = self.request.matchdict['asset_type'] if 'asset_type' in self.request.matchdict else None

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
        assets = DBSession().query(Asset).order_by(desc(Asset.id)).all()

        return dict(
            assets=assets
        )

    @view_config(route_name="asset_form", renderer='altaircms:templates/asset/form.mako')
    def asset_form(self):
        def succeed(request, captured):
            # @TODO: S3に対応する
            today = date.today().strftime('%Y-%m-%d')
            storepath = os.path.join(get_storepath(request),  today)
            if not os.path.exists(storepath):
                os.makedirs(storepath)

            original_filename = captured['uploadfile']['filename']
            filename = '%s.%s' % (uuid4(), original_filename[original_filename.rfind('.') + 1:])
            f = open(os.path.join(storepath, filename), 'wb')
            f.write(captured['uploadfile']['fp'].read())

            mimetype = detect_mimetype(filename)

            if captured['type'] == 'image':
                asset = ImageAsset(filepath=os.path.join(today, filename), mimetype=mimetype)
            elif captured['type'] == 'movie':
                asset = MovieAsset(filepath=os.path.join(today, filename), mimetype=mimetype)
            elif captured['type'] == 'flash':
                asset = FlashAsset(filepath=os.path.join(today, filename))

            DBSession.add(asset)

            return self.response_json_ok()

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

    @view_config(route_name="asset_view")
    def asset_view(self):
        if not self.asset:
            return NotFound()

        filepath = os.path.join(get_storepath(self.request), self.asset.filepath)
        content_type = self.asset.mimetype if self.asset.mimetype else 'application/octet-stream'

        return Response(file(filepath).read(), content_type=content_type)