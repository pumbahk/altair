# -*- coding:utf-8 -*-
import wtforms.ext.sqlalchemy.fields as extfields
import wtforms.form as form
import wtforms.fields as fields
import wtforms.validators as validators
import wtforms.widgets as widgets

from .models import Topcontent


def existing_image_assets():
    from altaircms.asset.models import ImageAsset
    return ImageAsset.query

def existing_pages():
    ##本当は、client.id, site.idでfilteringする必要がある
    ##本当は、日付などでfilteringする必要がある
    from altaircms.page.models import Page
    return Page.query

class TopcontentForm(form.Form):
    title = fields.TextField(label=u"タイトル", validators=[validators.Required()])
    # is_global = fields.BooleanField(label=u"全体に公開", default=True)
    publish_open_on = fields.DateTimeField(label=u"公開開始日")
    publish_close_on = fields.DateTimeField(label=u"公開終了日")
    text = fields.TextField(label=u"内容", validators=[validators.Required()], widget=widgets.TextArea())
    
    orderno = fields.IntegerField(label=u"表示順序", default=50)
    is_vetoed = fields.BooleanField(label=u"公開禁止")

    page = extfields.QuerySelectField(
        label=u"ページ", query_factory=existing_pages, allow_blank=True)
    image_asset = extfields.QuerySelectField(
        label=u"画像", query_factory=existing_image_assets, allow_blank=True)
    kind = fields.SelectField(label=u"種別", choices=[(x, x) for x in Topcontent.KIND_CANDIDATES])
    countdown_type = fields.SelectField(label=u"カウントダウンの種別", choices=Topcontent.COUNTDOWN_CANDIDATES)    
    
