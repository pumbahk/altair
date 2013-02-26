# coding: utf-8
import os
import logging
import re
import sqlalchemy as sa
from collections import defaultdict
from datetime import datetime
from webob.multidict import MultiDict
from altaircms.formhelpers import Form
from wtforms import fields
from wtforms import widgets
from wtforms import validators
from altaircms.layout.models import Layout
from .models import Page
from .models import PageSet
from .models import PageType
from altaircms.event.models import Event
from altaircms.interfaces import IForm
from altaircms.interfaces import implementer
from altaircms.formhelpers import dynamic_query_select_field_factory
from altaircms.formhelpers import append_errors
from altaircms.formhelpers import MaybeDateTimeField
from pyramid.threadlocal import get_current_request
logger = logging.getLogger(__name__)

from ..models import Category, Genre
from .api import get_static_page_utility
from . import writefile

class PageSetSearchForm(Form):
    """
    検索対象: category,  name,  公開停止中, 
    """
    freeword = fields.TextField(label=u'タイトル, サブタイトルなど')
    is_vetoed = fields.BooleanField(label=u"検索対象から除外したものだけを探す")
    category = dynamic_query_select_field_factory(
        Category, allow_blank=True, label=u"カテゴリ",
        get_label=lambda obj: obj.label or u"--なし--")

def url_field_validator(form, field):
    ## conflictチェックも必要
    if field.data.startswith("/") or "://" in field.data :
        raise validators.ValidationError(u"先頭に/をつけたり, http://foo.bar.comのようなurlにはしないでください.(正しい例:top/music/abc)")

def url_not_conflict(form, field):
    if form.data.get('add_to_pagset'):
        return 
    ## fixme
    request = get_current_request()
    ####
    qs = PageSet.query.filter_by(url=field.data, organization_id=request.organization.id)
    if request.matchdict.get("page_id") or request.matchdict.get("id"):
        pk = request.matchdict.get("page_id") or request.matchdict.get("id")
        page = Page.query.filter_by(id=pk).first()
        qs = qs.filter(PageSet.id!=page.pageset_id)

    if qs.count() > 0:
        raise validators.ValidationError(u'URL "%s" は既に登録されてます' % field.data)

def pagetype_filter(model, request, query):
    return query.filter_by(name=request.GET["pagetype"])

class PageInfoSetupForm(Form):
    """ このフォームを使って、PageFormへのデフォルト値を挿入する。
    """
    pagetype = dynamic_query_select_field_factory(PageType, allow_blank=False, label=u"ページタイプ", 
                                                  get_label=lambda o: o.label, 
                                                  dynamic_query=pagetype_filter)
    genre = dynamic_query_select_field_factory(Genre, allow_blank=True, label=u"ジャンル", 
                                               get_label=lambda g: g.label)
    name = fields.TextField(label=u"名前", validators=[validators.Required()])

class PageInfoSetupWithEventForm(Form):
    event = dynamic_query_select_field_factory(Event, allow_blank=True, label=u"イベント", 
                                               get_label=lambda obj:  obj.title)
    pagetype = dynamic_query_select_field_factory(PageType, allow_blank=False, label=u"ページタイプ", 
                                                  get_label=lambda o: o.label, 
                                                  dynamic_query=pagetype_filter)
    genre = dynamic_query_select_field_factory(Genre, allow_blank=True, label=u"ジャンル", 
                                               get_label=lambda g: g.label)
    name = fields.TextField(label=u"名前", validators=[validators.Required()])

@implementer(IForm)
class PageForm(Form):
    def layout_filter(model, request, query):
        pagetype = PageType.get_or_create(name=request.GET["pagetype"], organization_id=request.organization.id)
        return request.allowable(Layout).with_transformation(Layout.applicable(pagetype.id))
    name = fields.TextField(label=u"名前", validators=[validators.Required()])
    url = fields.TextField(validators=[url_field_validator,  url_not_conflict],label=u"URL", )
    genre = dynamic_query_select_field_factory(Genre, allow_blank=True, label=u"ジャンル", 
                                               get_label=lambda g: g.label)
    pageset = dynamic_query_select_field_factory(PageSet, allow_blank=True, label=u"ページセット",
                                                 get_label=lambda ps: ps.name)
    pagetype = dynamic_query_select_field_factory(PageType, allow_blank=False, label=u"ページタイプ", 
                                                  get_label=lambda o: o.label, 
                                                  dynamic_query=pagetype_filter)
    title = fields.TextField(label=u"ページタイトル", validators=[validators.Required()])

    description = fields.TextField(label=u"概要", widget=widgets.TextArea())
    keywords = fields.TextField(widget=widgets.TextArea())
    tags = fields.TextField(label=u"タグ(区切り文字:\",\")")
    private_tags = fields.TextField(label=u"非公開タグ(区切り文字:\",\")")
    layout = dynamic_query_select_field_factory(Layout, allow_blank=False, 
                                                get_label=lambda obj: u"%s(%s)" % (obj.title, obj.template_filename), 
                                                dynamic_query=layout_filter
                                                )
    # event_id = fields.IntegerField(label=u"", widget=widgets.HiddenInput())
    event = dynamic_query_select_field_factory(Event, allow_blank=True, label=u"イベント", 
                                               get_label=lambda obj:  obj.title)
    parent = dynamic_query_select_field_factory(PageSet, 
                                                allow_blank=True, label=u"親ページ", 
                                                get_label=lambda obj:  u'%s' % obj.name)

    publish_begin = fields.DateTimeField(label=u"掲載開始", validators=[validators.Required()])
    publish_end = MaybeDateTimeField(label=u"掲載終了")


    add_to_pagset = fields.BooleanField(label=u"既存のページセットに追加")

    def validate(self, **kwargs):
        """ override to form validation"""
        super(PageForm, self).validate()
        data = self.data
        if data["publish_end"] and data["publish_begin"]:
            if data["publish_begin"] > data["publish_end"]:
                append_errors(self.errors, "publish_begin", u"開始日よりも後に終了日が設定されています")

        if (self.data.get('url') and self.data.get('pageset')):
            urlerrors = self.errors.get('url', [])
            urlerrors.append(u'URLの一部かページセットのどちらかを指定してください。')
            self.errors['url'] = urlerrors
        return not bool(self.errors)


@implementer(IForm)
class PageUpdateForm(Form):
    name = fields.TextField(label=u"名前", validators=[validators.Required()])
    url = fields.TextField(validators=[url_field_validator, url_not_conflict],
                           label=u"URL", 
                           widget=widgets.TextArea())

    title = fields.TextField(label=u"ページタイトル", validators=[validators.Required()], widget=widgets.TextArea())
    description = fields.TextField(label=u"概要", widget=widgets.TextArea())
    keywords = fields.TextField(widget=widgets.TextArea())
    layout = dynamic_query_select_field_factory(Layout, allow_blank=False, 
                                                get_label=lambda obj: u"%s" % obj.title)
    event = dynamic_query_select_field_factory(Event, allow_blank=True, label=u"イベント", 
                                               get_label=lambda obj:  obj.title)
    pageset = dynamic_query_select_field_factory(PageSet, allow_blank=True, label=u"ページセット",
                                                 get_label=lambda ps: ps.name)
    parent = dynamic_query_select_field_factory(PageSet, 
                                                allow_blank=True, label=u"親ページ", 
                                                get_label=lambda obj:  u'%s' % obj.name)

    publish_begin = MaybeDateTimeField(label=u"掲載開始")
    publish_end = MaybeDateTimeField(label=u"掲載終了")

    def validate(self):
        """ override to form validation"""
        result = super(PageUpdateForm, self).validate()

        data = self.data
        if data.get("publish_end"):
            if data["publish_begin"] > data["publish_end"]:
                append_errors(self.errors, "publish_begin", u"開始日よりも後に終了日が設定されています")

        # if (self.data.get('url') and self.data.get('pageset')) or (not self.data.get('url') and not self.data.get('pageset')):
        #     urlerrors = self.errors.get('url', [])
        #     urlerrors.append(u'URLの一部かページセットのどちらかを指定してください。')
        #     self.errors['url'] = urlerrors

        return not bool(self.errors)

begin_regex = re.compile(r'begin_(?P<page_id>\d+)')
end_regex = re.compile(r'end_(?P<page_id>\d+)')
published_regex = re.compile(r'published_(?P<page_id>\d+)')

class PageSetFormProxy(object):
    def __init__(self, pageset):
        self.__dict__['_pageset'] = pageset
        logger.debug(self._pageset)

    def get_page(self, page_id):
        for page in self._pageset.pages:
            if str(page.id) == page_id:
                return page

    def __setattr__(self, name, value):

        self.set_page_publishing(name, value, begin_regex.match, "publish_begin")
        self.set_page_publishing(name, value, end_regex.match, "publish_end")

    def set_page_publishing(self, name, value, matcher, attr_name):
        m = matcher(name)
        if m is not None:
            page = self.get_page(m.groupdict()['page_id'])
            maybe_set_attr(page, attr_name, value)

def maybe_set_attr(obj, name, value):
    if obj is None:
        return
    setattr(obj, name, value)

def validate_page_publishings_overlapping(publishings):
    """ 重複期間チェック 
    開始日終了日間に入る他の開始日がないこと
    """
    real_publishings = [p for p in publishings.values() if p["end"] and p["published"]]
    for publishing in real_publishings:
        page_id = publishing['page_id']
        begin = publishing['begin']
        end = publishing['end']
        res = any([in_term(other_pub, begin) for other_pub in real_publishings if other_pub['page_id'] != page_id])
        if res:
            return False # TODO エラーになった箇所を特定する
    return True

def in_term(publishing, date):
    return publishing['begin'] <= date < publishing['end']


def validate_page_publishings_connected(publishings):
    """ 連続性チェック
    すべての終了日の次の日に対応する開始日があること
    """
    real_publishings = [p for p in publishings.values() if p["begin"] and p["published"]]
    last_start = max(p["begin"] for p in real_publishings)
    for publishing in real_publishings:
        if publishing["published"]:
            page_id = publishing['page_id']
            begin = publishing['begin']
            end = publishing['end']

            ## 最後のものは対応する開始日なしでOK
            if begin == last_start:
                continue
            res = not any([other_pub['begin'] == end 
                           for other_pub 
                           in real_publishings if other_pub['page_id'] != page_id])
            if res:
                return False # TDOO エラーになった箇所を特定する
    return True

def validate_page_publishings(publishings):
    return (validate_page_publishings_overlapping(publishings) 
            and validate_page_publishings_connected(publishings))

def pageset_form_validate(self):
    logger.debug('validate: %s' % self.data)
    result = Form.validate(self)
    page_publishings = defaultdict(dict)


    if result:
        for key, value in self.data.items():
            m = begin_regex.match(key)
            if m:
                page_id = m.groupdict()['page_id']
                page_publishing = page_publishings[page_id]
                page_publishing['begin'] = value
                page_publishing['page_id'] = page_id

            m = end_regex.match(key)
            if m:
                page_id = m.groupdict()['page_id']
                page_publishing = page_publishings[page_id]
                page_publishing['end'] = value
                page_publishing['page_id'] = page_id

            m = published_regex.match(key)
            if m:
                page_id = m.groupdict()['page_id']
                page_publishing = page_publishings[page_id]
                page_publishing['published'] = value == "True" ## ugly
                page_publishing['page_id'] = page_id
        # if not (result and validate_page_publishings(page_publishings)):
        #     raise Exception
        # return True
                
        return result and validate_page_publishings(page_publishings)

    return result



class PageSetFormFactory(object):
    def __init__(self, request):
        self.request = request

    def __call__(self, pageset, base_form=Form):
        props = {}
        data = MultiDict()
        for page in pageset.pages:
            page_id = page.id
            if page.published:
                props['begin_%d' % page_id] = fields.DateTimeField(u"")
            else:
                props['begin_%d' % page_id] = MaybeDateTimeField(u"")
            props['end_%d' % page_id] = MaybeDateTimeField(u"")
            props['published_%d' % page_id] = fields.HiddenField(u"")
            data['begin_%d' % page_id] = page.publish_begin.strftime("%Y-%m-%d %H:%M:%S") if page.publish_begin else ""
            data['end_%d' % page_id] = page.publish_end.strftime("%Y-%m-%d %H:%M:%S") if page.publish_end else ""
            data["published_%d" % page_id] = page.published

        props['validate'] = pageset_form_validate
        PageSetForm = type('PageSetForm',
                           (base_form,),
                           props)
        logger.debug(self.request.method)
        if self.request.method == "POST":
            logger.debug(self.request.POST)
            return PageSetForm(formdata=self.request.POST)
        else:
            return PageSetForm(formdata=data)


    def published(self, form, page):
        return getattr(form, 'published_%d' % page.id)

    def publish_begin(self, form, page):
        return getattr(form, 'begin_%d' % page.id)

    def publish_end(self, form, page):
        return getattr(form, 'end_%d' % page.id)


## static page
class StaticPageCreateForm(Form):
    name = fields.TextField(label=u"name", validators=[validators.Required()])
    zipfile = fields.FileField(label=u"zipファイルを投稿")

    def validate(self, request):
        status = super(type(self), self).validate()
        static_directory = get_static_page_utility(request)
        path = os.path.join(static_directory.get_base_directory(), self.data["name"])
        if os.path.exists(path):
            append_errors(self.errors, "name", u"%sは既に存在しています。他の名前で登録してください" % self.data["name"])
            status = False
        if self.data["zipfile"] == u"":
            message = u"zipfileではありません。.zipの拡張子が付いたファイルを投稿してください" 
            append_errors(self.errors, "zipfile", message)
            status = False
        elif not writefile.is_zipfile(self.data["zipfile"].file):
            message = u"%sはzipfileではありません。.zipの拡張子が付いたファイルを投稿してください" % (self.data["zipfile"].filename)
            append_errors(self.errors, "zipfile", message)
            status = False
        return status
