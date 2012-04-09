# coding: utf-8
import json
import os
from datetime import date
from uuid import uuid4
from .models import ImageAsset #boo
from altaircms.lib.viewhelpers import FlashMessage

from pyramid.exceptions import NotFound
from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response
from pyramid.view import view_config
from pyramid.view import view_defaults
from altaircms.lib.fanstatic_decorator import with_bootstrap
from altaircms.asset import get_storepath, detect_mimetype

@view_config(route_name="asset_list", renderer="altaircms:templates/asset/list.mako", 
             decorator=with_bootstrap,)
def list(request):
    assets = request.context.get_assets()
    form = request.context.get_form()
    return {"assets": assets, "form": form}

@view_config(route_name="asset_view", renderer='altaircms:templates/asset/view.mako', 
             decorator=with_bootstrap, request_method='GET')
def view(request):
    # if not all(k in request.matchdict for k in  ("asset_id", "asset_type")):
    if not "asset_id" in request.matchdict:
        return NotFound()
    asset = request.context.get_asset(request.matchdict["asset_id"])
    return {"asset": asset}

# @view_defaults(route_name="asset_delete", permission="asset_delete", decorator=with_bootstrap)
@view_defaults(route_name="asset_delete",  decorator=with_bootstrap)
class DeleteView(object):
    def __init__(self, request):
        self.request = request

    @view_config(request_method="GET", renderer="altaircms:templates/asset/delete_confirm.mako")
    def confirm(self):
        asset = self.request.context.get_asset(self.request.matchdict["asset_id"])
        return {"asset": asset}

    @view_config(request_method="POST", renderer="altaircms:templates/asset/delete_confirm.mako")
    def execute(self):
        # 削除処理
        context = self.request.context
        asset = context.get_asset(self.request.matchdict["asset_id"])
        storepath = context.get_asset_storepath()
        context.delete_asset_file(storepath, asset.filepath)
        asset = self.request.context.get_asset(self.request.matchdict["asset_id"])
        self.request.context.DBSession.delete(asset)
        FlashMessage.success("asset deleted", request=self.request)
        return HTTPFound(self.request.route_path("asset_list"))
    
# @view_defaults(route_name="asset_create", permission="asset_create", decorator=with_bootstrap)
@view_defaults(route_name="asset_create", decorator=with_bootstrap)
class CreateView(object):
    def __init__(self, request):
        self.request = request

    # @view_config(request_method="GET", renderer="altaircms:templates/asset/create_confirm.mako")
    # def confirm(self):
    #     form = self.request.context.get_form(data=self.request.GET)
    #     return {"form": form}

    @view_config(request_method="POST")
    def execute(self):
        context = self.request.context
        form = context.get_form(data=self.request.POST)
        if form.validate():
            original_filename = form.data["filepath"].filename
            storepath = context.get_asset_storepath()
            creator = context.write_asset_file(storepath, original_filename, form.data["filepath"].file)
            create = creator.create_asset_function(self.request.matchdict["asset_type"])
            asset = create(dict(alt=form.data["alt"], mimetype=detect_mimetype(original_filename))) ## tag

            self.request.context.DBSession.add(asset)
            FlashMessage.success("asset deleted", request=self.request)    
        else:
            FlashMessage.error(str(form.errors), request=self.request)    
        return HTTPFound(self.request.route_path("asset_list"))


# @view_defaults(route_name="asset_update", permission="asset_update", decorator=with_bootstrap)
# class UpdateView(object):
#     def __init__(self, request):
#         self.request = request

# @view_config(route_name="asset_display", permission="asset_read", request_method="GET")
@view_config(route_name="asset_display", request_method="GET")
def asset_display(request):
    """ display asset as image(image, flash, movie)
    """
    ## todo refactoring
    asset = request.context.get_asset(request.matchdict["asset_id"])

    attr = request.GET.get("filepath") or "filepath"
    filepath = getattr(asset, attr)
    filepath = os.path.join(get_storepath(request), filepath)
    content_type = asset.mimetype if asset.mimetype else 'application/octet-stream'
    if os.path.exists(filepath):
        return Response(file(filepath).read(), content_type=content_type)
    else:
        return Response("", content_type=content_type)


# @view_defaults(decorator=with_bootstrap)
# class AssetEditView(object):
#     def __init__(self, request):
#         self.request = request
#         self.asset_id = self.request.matchdict['asset_id'] if 'asset_id' in self.request.matchdict else None
#         self.asset = DBSession.query(Asset).get(self.asset_id) if self.asset_id else None
#         self.asset_type = self.request.matchdict['asset_type'] if 'asset_type' in self.request.matchdict else None

#     def response_json_ok(self):
#         # @TODO: 他のAPI呼び出しなどと共通化する
#         content = json.dumps(dict(status='OK'))
#         content_type = 'application/json'
#         return Response(content, content_type=content_type)

#     def render_form(self, form, appstruct=colander.null, submitted='submit',
#                     success=None, readonly=False):
#         captured = None
#         if submitted in self.request.POST:
#             try:
#                 controls = self.request.POST.items()
#                 captured = form.validate(controls)
#                 if success:
#                     response = success(self.request, captured)
#                     if response is not None:
#                         return response
#                 html = markupsafe.Markup(form.render(captured))
#             except ValidationFailure, e:
#                 html = markupsafe.Markup(e.render())

#         else:
#             if not appstruct:
#                 appstruct = {'type': self.asset_type}
#             html = markupsafe.Markup(form.render(appstruct))

#         if self.request.is_xhr:
#             return Response(html)

 
#         # values passed to template for rendering
#         return {
#             'form':html,
#             'captured':repr(captured),
#             'asset_type': self.asset_type,
#             }

#     @view_config(route_name='asset_list', renderer='altaircms:templates/asset/list.mako', request_method='GET', permission='asset_read')
#     def list_(self):
#         assets = DBSession().query(Asset).order_by(desc(Asset.id)).all()

#         return dict(
#             assets=assets
#         )

#     @view_config(route_name="asset_form", renderer='altaircms:templates/asset/form.mako', permission='asset_update')
#     def asset_form(self):
#         def succeed(request, captured):
#             # @TODO: S3に対応する
#             today = date.today().strftime('%Y-%m-%d')
#             storepath = os.path.join(get_storepath(request),  today)
#             if not os.path.exists(storepath):
#                 os.makedirs(storepath)

#             original_filename = captured['uploadfile']['filename']
#             filename = '%s.%s' % (uuid4(), original_filename[original_filename.rfind('.') + 1:])
#             filepath = os.path.join(storepath, filename)

#             buf = captured['uploadfile']['fp'].read()
#             size = len(buf)
#             dst_file = open(filepath, 'w+b')
#             dst_file.write(buf)
#             dst_file.seek(0)

#             mimetype = detect_mimetype(filename)

#             if captured['type'] == 'image':
#                 (width, height) = Image.open(dst_file.name).size
#                 asset = ImageAsset(
#                     filepath=os.path.join(today, filename),
#                     mimetype=mimetype,
#                     width=width,
#                     height=height,
#                     alt=captured.get('alt', '')
#                 )
#             elif captured['type'] == 'movie':
#                 asset = MovieAsset(filepath=os.path.join(today, filename), mimetype=mimetype)
#             elif captured['type'] == 'flash':
#                 from .swfrect import get_swf_rect, rect_to_size, in_pixel
#                 (width, height) = in_pixel(rect_to_size(get_swf_rect(dst_file.name)))
#                 asset = FlashAsset(
#                     filepath=os.path.join(today, filename),
#                     width=width,
#                     height=height
#                 )

#             asset.size = size
#             DBSession.add(asset)

#             return self.response_json_ok()

#         if self.asset_type not in ASSET_TYPE:
#             return NotFound()

#         cls = globals()[self.asset_type.capitalize() + 'AssetSchema']()
#         form = Form(cls, buttons=('submit', ), use_ajax=False)

#         return self.render_form(form, success=succeed)

#     @view_config(route_name="asset_edit", permission='asset_update',
#         renderer='altaircms:templates/asset/view.mako', request_method='GET')
#     def asset_edit(self):
#         if not self.asset:
#             return NotFound()

#         if 'raw' in self.request.params:
#             filepath = os.path.join(get_storepath(self.request), self.asset.filepath)
#             content_type = self.asset.mimetype if self.asset.mimetype else 'application/octet-stream'

#             return Response(file(filepath).read(), content_type=content_type)

#         return dict(
#             asset=self.asset
#         )

#     @view_config(route_name="asset_edit", request_method='POST', permission="asset_delete")
#     def asset_delete(self):
#         if not self.asset:
#             return NotFound()

#         if '_method' in self.request.params and self.request.params['_method'].lower() == 'delete':
#             # 削除処理
#             filename = os.path.join(get_storepath(self.request), self.asset.filepath)
#             if os.path.exists(filename):
#                 os.remove(filename)
#             DBSession.delete(self.asset)

#             return self.response_json_ok()
#         else:
#             # 更新処理
#             pass


# class AssetRESTAPIView(BaseRESTAPI):
#     model = ImageAsset
#     form = ImageAssetForm

#     object_mapper = ImageAssetMapper

#     def __init__(self, request, *args, **kwargs):
#         #self.validation_schema = ImageAssetSchema # @TODO: 切り替えられるようにする
#         super(AssetRESTAPIView, self).__init__(request, *args, **kwargs)

#     #@view_config(renderer='json')
#     def create(self):
#         return super(AssetRESTAPIView, self).create()

#     #@view_config(renderer='json')
#     def read(self):
#         self.model_object = self.get_object_by_id(self.id)
#         super(AssetRESTAPIView, self).read()
#         return self.object_mapper(self.model_object).as_dict()

#     #@view_config(renderer='json')
#     def update(self):
#         self.model_object = self.get_object_by_id(self.id)
#         return super(AssetRESTAPIView, self).update()

#     #@view_config(renderer='json')
#     def delete(self):
#         self.model_object = self.get_object_by_id(self.id)
#         return super(AssetRESTAPIView, self).delete()

#     def _get_mapper(self):
#         mapper = globals()[self.model.__name__ + 'Mapper']
#         return mapper

#     def get_object_by_id(self, id):
#         try:
#             model_object = self.session.query(self.model).get(id)
#             return model_object
#         except:
#             return None
