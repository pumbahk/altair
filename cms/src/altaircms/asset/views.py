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

from altaircms.models import DBSession
from altaircms.views import BaseRESTAPI

from altaircms.asset import get_storepath
from altaircms.asset.models import Asset, ImageAsset, MovieAsset, FlashAsset
from altaircms.asset.forms import *
from altaircms.asset.mappers import *
from altaircms.asset.forms import ImageAssetForm


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
    return EXT_MAP[ext] if ext in EXT_MAP else 'application/octet-stream'


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

    @view_config(route_name='asset_list', renderer='altaircms:templates/asset/list.mako', request_method='GET', permission='edit')
    def list_(self):
        assets = DBSession().query(Asset).order_by(desc(Asset.id)).all()

        return dict(
            assets=assets
        )

    @view_config(route_name="asset_form", renderer='altaircms:templates/asset/form.mako', permission='edit')
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

    @view_config(route_name="asset_edit", permission='edit',
        renderer='altaircms:templates/asset/view.mako', request_method='GET')
    def asset_edit(self):
        if not self.asset:
            return NotFound()

        if 'raw' in self.request.params:
            filepath = os.path.join(get_storepath(self.request), self.asset.filepath)
            content_type = self.asset.mimetype if self.asset.mimetype else 'application/octet-stream'

            return Response(file(filepath).read(), content_type=content_type)

        return dict(
            asset=self.asset
        )

    @view_config(route_name="asset_edit", permission='edit', request_method='POST')
    def asset_delete(self):
        if not self.asset:
            return NotFound()

        if '_method' in self.request.params and self.request.params['_method'].lower() == 'delete':
            # 削除処理
            os.remove(os.path.join(get_storepath(self.request), self.asset.filepath))
            DBSession.delete(self.asset)

            return self.response_json_ok()
        else:
            # 更新処理
            pass




class AssetRESTAPIView(BaseRESTAPI):
    model = ImageAsset
    form = ImageAssetForm

    object_mapper = ImageAssetMapper

    def __init__(self, request, *args, **kwargs):
        #self.validation_schema = ImageAssetSchema # @TODO: 切り替えられるようにする
        super(AssetRESTAPIView, self).__init__(request, *args, **kwargs)

    #@view_config(renderer='json')
    def create(self):
        return super(AssetRESTAPIView, self).create()

    #@view_config(renderer='json')
    def read(self):
        self.model_object = self.get_object_by_id(self.id)
        super(AssetRESTAPIView, self).read()
        return self.object_mapper(self.model_object).as_dict()

    #@view_config(renderer='json')
    def update(self):
        self.model_object = self.get_object_by_id(self.id)
        return super(AssetRESTAPIView, self).update()

    #@view_config(renderer='json')
    def delete(self):
        self.model_object = self.get_object_by_id(self.id)
        return super(AssetRESTAPIView, self).delete()

    def _get_mapper(self):
        mapper = globals()[self.model.__name__ + 'Mapper']
        return mapper

    def get_object_by_id(self, id):
        try:
            model_object = self.session.query(self.model).get(id)
            return model_object
        except:
            return None
