# coding: utf-8
from wtforms.form import Form
from wtforms import fields
from wtforms import widgets
from wtforms import validators
from altaircms.layout.models import Layout
from altaircms.page.models import Page
from altaircms.event.models import Event
from altaircms.interfaces import IForm
from altaircms.interfaces import implementer
from altaircms.lib.formhelpers import dynamic_query_select_field_factory

"""
def json_validator(node, value):
    try:
        json.loads(value)
    except ValueError:
        raise colander.Invalid(node, 'JSON object required')

class PageSchema(colander.MappingSchema):
    url = colander.SchemaNode(colander.String())
    title = colander.SchemaNode(colander.String())
    description = colander.SchemaNode(colander.String(), missing='')
    keywords = colander.SchemaNode(colander.String(), missing='')
    tags = colander.SchemaNode(colander.String(), missing='') # タグマスタと紐付ける用。ajaxで書いたほうがいいかも

    layout_id = colander.SchemaNode(colander.Integer())
    # structure = colander.SchemaNode(colander.String(), validator=json_validator,
    #                                 widget=deform.widget.TextAreaWidget())
"""

def url_field_validator(form, field):
    ## conflictチェックも必要
    if field.data.startswith("/") or "://" in field.data :
        raise validators.ValidationError(u"先頭に/をつけたり, http://foo.bar.comのようなurlにはしないでください.(正しい例:top/music/abc)")

def url_not_conflict(form, field):
    if Page.query.filter_by(url=field.data).count() > 0:
        raise validators.ValidationError(u"%sは既に登録されてます" % field.data)

@implementer(IForm)
class PageForm(Form):
    # url = fields.TextField(validators=[url_field_validator], placeholder="top/music/abc")
    url = fields.TextField(validators=[ validators.Required(), url_field_validator],
                           label=u"URLの一部(e.g. top/music)")
    title = fields.TextField(label=u"ページタイトル", validators=[validators.Required()])
    description = fields.TextField(label=u"概要")
    keywords = fields.TextField()
    tags = fields.TextField(label=u"タグ")
    unpublic_tags = fields.TextField(label=u"非公開タグ")
    layout = dynamic_query_select_field_factory(Layout, allow_blank=False)
    # event_id = fields.IntegerField(label=u"", widget=widgets.HiddenInput())
    event = dynamic_query_select_field_factory(Event, allow_blank=True, label=u"イベント")
    parent = dynamic_query_select_field_factory(Page, allow_blank=True, label=u"親ページ")

