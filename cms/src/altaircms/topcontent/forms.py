# -*- coding:utf-8 -*-

import wtforms.form as form
import wtforms.fields as fields
import wtforms.validators as validators
import wtforms.widgets as widgets

from altaircms.lib.formhelpers import dynamic_query_select_field_factory
from altaircms.page.models import Page
from altaircms.asset.models import ImageAsset
from .models import Topcontent

class TopcontentForm(form.Form):
    title = fields.TextField(label=u"タイトル", validators=[validators.Required()])
    # is_global = fields.BooleanField(label=u"全体に公開", default=True)
    publish_open_on = fields.DateTimeField(label=u"公開開始日")
    publish_close_on = fields.DateTimeField(label=u"公開終了日")
    text = fields.TextField(label=u"内容", validators=[validators.Required()], widget=widgets.TextArea())
    
    orderno = fields.IntegerField(label=u"表示順序(1〜100)", default=50)
    is_vetoed = fields.BooleanField(label=u"公開禁止")

    ##本当は、client.id, site.idでfilteringする必要がある
    page = dynamic_query_select_field_factory(Page, label=u"ページ", allow_blank=True)
    image_asset = dynamic_query_select_field_factory(ImageAsset,label=u"画像", allow_blank=True)
    kind = fields.SelectField(label=u"種別", choices=[(x, x) for x in Topcontent.KIND_CANDIDATES])
    countdown_type = fields.SelectField(label=u"カウントダウンの種別", choices=Topcontent.COUNTDOWN_CANDIDATES)    
    
