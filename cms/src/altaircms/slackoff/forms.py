# -*- coding:utf-8 -*-
from wtforms.form import Form
from wtforms import fields
from wtforms import widgets
from wtforms import validators
import wtforms.ext.sqlalchemy.fields as extfields

from altaircms.event.models import Event
from altaircms.lib.formhelpers import dynamic_query_select_field_factory
from altaircms.helpers.formhelpers import required_field

from altaircms.plugins.widget.promotion.models import Promotion
from altaircms.models import Category
from altaircms.asset.models import ImageAsset
from altaircms.page.models import PageSet

class PerformanceForm(Form):
    backend_performance_id = fields.IntegerField(validators=[required_field()], label=u"バックエンド管理番号")
    event = dynamic_query_select_field_factory(Event, allow_blank=False, label=u"イベント", get_label=lambda obj: obj.title)
    title = fields.TextField(label=u"講演タイトル")
    venue = fields.TextField(label=u"開催場所")
    open_on = fields.DateTimeField(label=u"開場時間", validators=[required_field()])
    start_on = fields.DateTimeField(label=u"開始時間", validators=[required_field()])
    close_on = fields.DateTimeField(label=u"終了時間", validators=[required_field()])

class TicketForm(Form):
    orderno = fields.IntegerField(label=u"表示順序", validators=[required_field()])
    event = dynamic_query_select_field_factory(Event, allow_blank=False, label=u"イベント", get_label=lambda obj: obj.title) ## performance?
    price = fields.IntegerField(validators=[required_field()], label=u"料金")
    seattype = fields.TextField(validators=[required_field()], label=u"席種／グレード")

class PromotionUnitForm(Form):
    promotion = extfields.QuerySelectField(id="promotion", label=u"プロモーション枠", 
                                           get_label=lambda obj: obj.name, 
                                           query_factory = lambda : Promotion.query)
    main_image = dynamic_query_select_field_factory(
        ImageAsset, allow_blank=False, label=u"メイン画像",
        get_label=lambda obj: obj.title or u"名前なし")
    thumbnail = dynamic_query_select_field_factory(
        ImageAsset, allow_blank=False, label=u"サブ画像(60x60)",
        get_label=lambda obj: obj.title or u"名前なし")
    text = fields.TextField(validators=[required_field()], label=u"画像下のメッセージ")
    
class PromotionForm(Form):
    name = fields.TextField(label=u"プロモーション枠名")
    ## site

class CategoryForm(Form):
    name = fields.TextField(label=u"カテゴリ名")
    orderno = fields.IntegerField(label=u"表示順序")
    parent = dynamic_query_select_field_factory(
        Category, allow_blank=False, label=u"親カテゴリ",
        get_label=lambda obj: obj.name or u"--なし--")

    hierarchy = fields.SelectField(label=u"階層", choices=[(x, x) for x in [u"大", u"中", u"小"]])
    label = fields.TextField(label=u"label")
    imgsrc = fields.TextField(imgsrc=u"imgsrc")
    url = fields.TextField(label=u"リンク(外部ページのURL)")
    pageset = dynamic_query_select_field_factory(
        PageSet, allow_blank=False, label=u"リンク先ページ(CMSで作成したもの)",
        get_label=lambda obj: obj.name or u"--なし--")
    ## site
