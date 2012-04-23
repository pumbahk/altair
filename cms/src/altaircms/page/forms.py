# coding: utf-8
import logging
from wtforms.form import Form
from wtforms import fields
from wtforms import widgets
from wtforms import validators
from altaircms.layout.models import Layout
from altaircms.page.models import Page
from altaircms.page.models import PageSet
from altaircms.event.models import Event
from altaircms.interfaces import IForm
from altaircms.interfaces import implementer
from altaircms.lib.formhelpers import dynamic_query_select_field_factory

def url_field_validator(form, field):
    ## conflictチェックも必要
    if field.data.startswith("/") or "://" in field.data :
        raise validators.ValidationError(u"先頭に/をつけたり, http://foo.bar.comのようなurlにはしないでください.(正しい例:top/music/abc)")

def url_not_conflict(form, field):
    if form.data.get('add_to_pagset'):
        return 
    if Page.query.filter_by(url=field.data).count() > 0:
        raise validators.ValidationError(u'URL "%s" は既に登録されてます' % field.data)

@implementer(IForm)
class PageForm(Form):
    url = fields.TextField(validators=[url_field_validator,  url_not_conflict],
                           label=u"URLの一部(e.g. top/music)")
    pageset = dynamic_query_select_field_factory(PageSet, allow_blank=True, label=u"ページセット",
                                                 get_label=lambda ps: ps.name)

    title = fields.TextField(label=u"ページタイトル", validators=[validators.Required()])
    description = fields.TextField(label=u"概要")
    keywords = fields.TextField()
    tags = fields.TextField(label=u"タグ")
    private_tags = fields.TextField(label=u"非公開タグ")
    layout = dynamic_query_select_field_factory(Layout, allow_blank=False, 
                                                get_label=lambda obj: u"%s(%s)" % (obj.title, obj.template_filename))
    # event_id = fields.IntegerField(label=u"", widget=widgets.HiddenInput())
    event = dynamic_query_select_field_factory(Event, allow_blank=True, label=u"イベント", 
                                               get_label=lambda obj:  obj.title)
    parent = dynamic_query_select_field_factory(Page, allow_blank=True, label=u"親ページ", 
                                                get_label=lambda obj:  u'%s(%s)' % (obj.title, obj.url))

    publish_begin = fields.DateTimeField(label=u"掲載開始")
    publish_end = fields.DateTimeField(label=u"掲載終了")


    add_to_pagset = fields.BooleanField(label=u"既存のページセットに追加")

    def validate(self):
        """ override to form validation"""
        result = super(PageForm, self).validate()

        if (self.data.get('url') and self.data.get('pageset')) or (not self.data.get('url') and not self.data.get('pageset')):
            urlerrors = self.errors.get('url', [])
            urlerrors.append(u'URLの一部かページセットのどちらかを指定してください。')
            self.errors['url'] = urlerrors

        return not bool(self.errors)


@implementer(IForm)
class PageUpdateForm(Form):
    url = fields.TextField(validators=[ validators.Required(), url_field_validator],
                           label=u"URLの一部(e.g. top/music)")
    title = fields.TextField(label=u"ページタイトル", validators=[validators.Required()])
    description = fields.TextField(label=u"概要")
    keywords = fields.TextField()
    tags = fields.TextField(label=u"タグ")
    private_tags = fields.TextField(label=u"非公開タグ")
    layout = dynamic_query_select_field_factory(Layout, allow_blank=False, 
                                                get_label=lambda obj: u"%s(%s)" % (obj.title, obj.template_filename))
    event = dynamic_query_select_field_factory(Event, allow_blank=True, label=u"イベント", 
                                               get_label=lambda obj:  obj.title)
    parent = dynamic_query_select_field_factory(Page, allow_blank=True, label=u"親ページ", 
                                                get_label=lambda obj:  u'%s(%s)' % (obj.title, obj.url))



