# -*- coding:utf-8 -*-
from .api import get_static_page_utility
from altaircms.filelib import zipupload
import os
from altaircms.formhelpers import Form
from wtforms import fields
from wtforms import widgets
from wtforms import validators
from ..models import StaticPage, StaticPageSet
from altaircms.formhelpers import dynamic_query_select_field_factory
from altaircms.formhelpers import MaybeDateTimeField
from altaircms.formhelpers.validations import validate_term, validate_filetype, validate_url
from altaircms.formhelpers.validations import ValidationQueue
from altaircms.layout.models import Layout
from altaircms.page.forms import layout_filter
from altaircms.viewlib import FlashMessage

## static page
class StaticPageCreateForm(Form):
    name = fields.TextField(label=u"urlの一部")
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

    def validate(self):
        queue = ValidationQueue()
        queue.enqueue("publish_begin", validate_term, begin="publish_begin", end="publish_end")
        queue.enqueue("name", validate_url, "name", u"階層を持たせるには、Zipの中にフォルダを作成してください。")
        queue.enqueue("zipfile", validate_filetype, "zipfile", failfn=lambda v: not zipupload.is_zipfile(v.file), 
                      message=u"zipfileではありません。.zipの拡張子が付いたファイルを投稿してください" )
        return super(type(self), self).validate() and queue(self.data, self.errors)

def validate_name_ascii(self, value):
    try:
        value.data.decode("ascii")
    except UnicodeEncodeError:
        raise validators.ValidationError(u"ファイル名は英数表記してください")

def validate_deletable_filename(self, value):
    if value.data.startswith("/"):
        raise validators.ValidationError(u"絶対パスは使えません")
    if "./" in value.data:
        raise validators.ValidationError(u"./ ../は使えません")

class StaticFileAddForm(Form):
    file = fields.FileField(label=u"ファイルを追加")
    name = fields.TextField(label=u"ファイル名", validators=[validate_name_ascii, validate_deletable_filename])

    def validate(self):
        status = super(type(self), self).validate()
        if not status:
            return status
        data = self.data
        if not self.name.data:
            self.name.data = self.file.data.filename
        if os.path.splitext(self.name.data)[1] == "":
            self.name.data = self.name.data + os.path.splitext(data["file"].filename)[1]
        return status

class StaticFileUpdateForm(Form):
    file = fields.FileField(label=u"ファイルを更新")
    name = fields.HiddenField(label=u"", validators=[validate_name_ascii, validate_deletable_filename])

class StaticDirectoryAddForm(Form):
    name = fields.TextField(label=u"ディレクトリ名", validators=[validate_name_ascii, validate_deletable_filename])

class StaticFileDeleteForm(Form):
    name = fields.HiddenField(label=u"")
    validate_name = validate_deletable_filename

class StaticDirectoryDeleteForm(Form):
    name = fields.HiddenField(label=u"")
    validate_name = validate_deletable_filename

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
    last_editor = fields.HiddenField(validators=[validators.Optional()])

    def configure(self, request):
        self.request = request
        self.static_directory = get_static_page_utility(request)

    __display_fields__ = ["name", "label", "layout", "publish_begin", "publish_end", "last_editor"]

    def validate(self):
        queue = ValidationQueue()
        queue.enqueue("publish_begin", validate_term, begin="publish_begin", end="publish_end")
        return super(type(self), self).validate() and queue(self.data, self.errors)



class StaticPageSetForm(Form):
    name = fields.TextField(label=u"name", validators=[validators.Required()])    
    url = fields.TextField(label=u"url")

    __display_fields__ = ["name", "url"]    

    def object_validate(self, obj):
        data = self.data
        if obj.url != data["url"]:
            if StaticPageSet.query.filter(StaticPageSet.organization_id==obj.organization_id,
                                          StaticPageSet.pagetype_id==obj.pagetype_id,
                                          StaticPageSet.url==data["url"], StaticPageSet.id!=obj.id).count() > 0:
                self.errors["url"] = [u"{0} は既に利用されています".format(data["url"])]
                return False
            FlashMessage.info(u"ファイルの置かれる位置を変更しようとしています。この処理には時間がかかることがあります", request=self.request)
        return True

    def configure(self, request):
        self.request = request
        self.static_directory = get_static_page_utility(request)


