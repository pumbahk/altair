# -*- coding:utf-8 -*-
from .api import get_static_page_utility
from altaircms.filelib import zipupload
import os
from altaircms.formhelpers import Form
from wtforms import fields
from wtforms import widgets
from wtforms import validators
from ..models import StaticPage
from altaircms.formhelpers import dynamic_query_select_field_factory
from altaircms.formhelpers import MaybeDateTimeField
from altaircms.formhelpers.validations import validate_term, validate_filetype
from altaircms.formhelpers.validations import ValidationQueue
from altaircms.layout.models import Layout
from altaircms.page.forms import layout_filter

## static page
class StaticPageCreateForm(Form):
    name = fields.TextField(label=u"name", validators=[validators.Required()])
    label = fields.TextField(label=u"タイトル", validators=[validators.Required()])
    zipfile = fields.FileField(label=u"zipファイルを投稿")
    layout = dynamic_query_select_field_factory(Layout, allow_blank=True, 
                                                get_label=lambda obj: u"%s(%s)" % (obj.title, obj.template_filename), 
                                                dynamic_query=layout_filter
                                                )
    publish_begin = fields.DateTimeField(label=u"掲載開始", validators=[validators.Optional()])
    publish_end = MaybeDateTimeField(label=u"掲載終了", validators=[validators.Optional()])
    interceptive = fields.BooleanField(label=u"同一urlのページセットを横取りする", default=True)


    def configure(self, request):
        self.request = request
        self.static_directory = get_static_page_utility(request)

    def _validate_root_directory(self, data):
        path = os.path.join(self.static_directory.get_base_directory(), data["name"])
        if os.path.exists(path):
            raise validators.ValidationError(u"{0} は既に利用されています".format(data["name"]))

    def validate(self):
        queue = ValidationQueue()
        queue.enqueue("publish_begin", validate_term, begin="publish_begin", end="publish_end")
        queue.enqueue("zipfile", validate_filetype, "zipfile", failfn=lambda v: not zipupload.is_zipfile(v.file), 
                      message=u"zipfileではありません。.zipの拡張子が付いたファイルを投稿してください" )
        queue.enqueue("name", self._validate_root_directory)
        return super(type(self), self).validate() and queue(self.data, self.errors)

class StaticPageForm(Form):
    name = fields.TextField(label=u"name", validators=[validators.Optional()])
    label = fields.TextField(label=u"タイトル", validators=[validators.Required()])
    layout = dynamic_query_select_field_factory(Layout, allow_blank=True, 
                                                get_label=lambda obj: u"%s(%s)" % (obj.title, obj.template_filename), 
                                                dynamic_query=layout_filter
                                                )
    publish_begin = fields.DateTimeField(label=u"掲載開始", validators=[validators.Optional()])
    publish_end = MaybeDateTimeField(label=u"掲載終了", validators=[validators.Optional()])
    interceptive = fields.BooleanField(label=u"同一urlのページセットを横取りする", default=True)

    def configure(self, request):
        self.request = request
        self.static_directory = get_static_page_utility(request)

    def object_validate(self, obj):
        self.request._static_page_name = obj.name #too add-hoc        
        return True

    def validate(self):
        status = super(type(self), self).validate()
        if not status:
            return False

        data = self.data
        if data.get("name") and hasattr(self, "static_directory"):
            path = os.path.join(self.static_directory.get_base_directory(), self.data["name"])
            if os.path.exists(path):
                if self.request.allowable(StaticPage).filter(StaticPage.name==self.data["name"], StaticPage.id!=self.request.matchdict["id"]).count() > 0:
                    append_errors(self.errors, "name", u"%sは既に存在しています。他の名前で登録してください" % self.data["name"])
                    status = False

        if data.get("publish_end") and data.get("publish_begin"):
            if data["publish_begin"] > data["publish_end"]:
                append_errors(self.errors, "publish_begin", u"開始日よりも後に終了日が設定されています")
        return status

    __display_fields__ = ["name", "label", "layout", "publish_begin", "publish_end", "interceptive"]

