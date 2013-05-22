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

class StaticUploadOnlyForm(Form):
    zipfile = fields.FileField(label=u"zipファイルを投稿")

    def configure(self, request):
        self.request = request
        self.static_directory = get_static_page_utility(request)

    def validate(self):
        queue = ValidationQueue()
        queue.enqueue("zipfile", validate_filetype, "zipfile", failfn=lambda v: not zipupload.is_zipfile(v.file), 
                      message=u"zipfileではありません。.zipの拡張子が付いたファイルを投稿してください" )
        return super(type(self), self).validate() and queue(self.data, self.errors)


class StaticPageForm(Form):
    name = fields.TextField(label=u"name", validators=[validators.Required()])
    label = fields.TextField(label=u"タイトル", validators=[validators.Required()])
    layout = dynamic_query_select_field_factory(Layout, allow_blank=True, 
                                                get_label=lambda obj: u"%s(%s)" % (obj.title, obj.template_filename), 
                                                dynamic_query=layout_filter
                                                )
    publish_begin = fields.DateTimeField(label=u"掲載開始", validators=[validators.Optional()])
    publish_end = MaybeDateTimeField(label=u"掲載終了", validators=[validators.Optional()])

    def configure(self, request):
        self.request = request
        self.static_directory = get_static_page_utility(request)

    __display_fields__ = ["name", "label", "layout", "publish_begin", "publish_end"]

    def validate(self):
        queue = ValidationQueue()
        queue.enqueue("publish_begin", validate_term, begin="publish_begin", end="publish_end")
        return super(type(self), self).validate() and queue(self.data, self.errors)



class StaticPageSetForm(Form):
    name = fields.TextField(label=u"name", validators=[validators.Required()])    
    url = fields.TextField(label=u"url", validators=[validators.Required()])

    __display_fields__ = ["name", "url"]    

    def object_validate(self, obj):
        data = self.data
        self.request._static_page_prefix = obj.url #too add-hoc    
        path = os.path.join(self.static_directory.get_base_directory(), data["url"])
        if obj.url != data["url"] and os.path.exists(path):
            self.errors["url"] = [u"{0} は既に利用されています".format(data["url"])]
            return False
        return True

    def configure(self, request):
        self.request = request
        self.static_directory = get_static_page_utility(request)


