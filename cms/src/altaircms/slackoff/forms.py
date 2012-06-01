# -*- coding:utf-8 -*-
from wtforms.form import Form
from wtforms import fields
from wtforms import widgets
from wtforms import validators
import wtforms.ext.sqlalchemy.fields as extfields


from altaircms.lib.formhelpers import dynamic_query_select_field_factory
from altaircms.helpers.formhelpers import required_field

from ..event.models import Event
from ..plugins.widget.promotion.models import Promotion
from ..models import Category
from ..asset.models import ImageAsset
from ..page.models import PageSet
from ..topic.models import Topic, Topcontent
from ..tag.models import PageTag


import pkg_resources
def import_symbol(symbol):
    return pkg_resources.EntryPoint.parse("x=%s" % symbol).load(False)


class LayoutForm(Form):
    title = fields.TextField(u'タイトル', validators=[validators.Required()])
    template_filename = fields.TextField(u'テンプレートファイル名', validators=[validators.Required()])
    blocks = fields.TextField(u'ブロック', validators=[validators.Required()])

    __display_fields__ = [u"title", u"template_filename", u"blocks"]
    
class PerformanceForm(Form):
    title = fields.TextField(label=u"講演タイトル")
    backend_id = fields.IntegerField(validators=[required_field()], label=u"バックエンド管理番号")
    event = dynamic_query_select_field_factory(Event, allow_blank=False, label=u"イベント", get_label=lambda obj: obj.title)
    prefecture = fields.SelectField(label=u"開催県", choices=import_symbol("altaircms.seeds.prefecture:PREFECTURE_CHOICES"))
    venue = fields.TextField(label=u"開催場所(詳細)")
    open_on = fields.DateTimeField(label=u"開場時間", validators=[required_field()])
    start_on = fields.DateTimeField(label=u"開始時間", validators=[required_field()])
    close_on = fields.DateTimeField(label=u"終了時間", validators=[required_field()])
    purchase_link = fields.TextField(label=u"購入ページリンク")

    __display_fields__ = [u"title", u"backend_id", u"event",
                          u"prefecture", u"venue", 
                          u"open_on", u"start_on", u"close_on",
                          u"purchase_link"]


class TicketForm(Form):
    event = dynamic_query_select_field_factory(Event, allow_blank=False, label=u"イベント", get_label=lambda obj: obj.title) ## performance?
    seattype = fields.TextField(validators=[required_field()], label=u"席種／グレード")
    price = fields.IntegerField(validators=[required_field()], label=u"料金")
    orderno = fields.IntegerField(label=u"表示順序", validators=[required_field()])

    __display_fields__ = [u"event", u"seattype", u"price", u"orderno"]

class PromotionUnitForm(Form):
    promotion = extfields.QuerySelectField(id="promotion", label=u"プロモーション枠", 
                                           get_label=lambda obj: obj.name, 
                                           query_factory = lambda : Promotion.query)
    main_image = dynamic_query_select_field_factory(
        ImageAsset, allow_blank=False, label=u"メイン画像",
        get_label=lambda obj: obj.title or u"名前なし")
    text = fields.TextField(validators=[required_field()], label=u"画像下のメッセージ")
    thumbnail = dynamic_query_select_field_factory(
        ImageAsset, allow_blank=False, label=u"サブ画像(60x60)",
        get_label=lambda obj: obj.title or u"名前なし")

    __display_fields__ = [u"promotion", u"main_image", u"text", u"thumbnail"]
    
class PromotionForm(Form):
    name = fields.TextField(label=u"プロモーション枠名")
    ## site
    __display_fields__ = [u"name"]

class CategoryForm(Form):
    name = fields.TextField(label=u"カテゴリ名")
    label = fields.TextField(label=u"label")
    parent = dynamic_query_select_field_factory(
        Category, allow_blank=False, label=u"親カテゴリ",
        get_label=lambda obj: obj.label or u"--なし--")

    hierarchy = fields.SelectField(label=u"階層", choices=[(x, x) for x in [u"大", u"中", u"小"]])
    imgsrc = fields.TextField(label=u"imgsrc(e.g. /static/ticketstar/img/common/header_nav_top.gif)")
    url = fields.TextField(label=u"リンク(外部ページのURL)")
    pageset = dynamic_query_select_field_factory(
        PageSet, allow_blank=False, label=u"リンク先ページ(CMSで作成したもの)",
        get_label=lambda obj: obj.name or u"--なし--")
    orderno = fields.IntegerField(label=u"表示順序")

    __display_fields__ = [u"name", u"label",
                          u"parent, "u"hierarchy", 
                          u"imgsrc", u"url", u"pageset", 
                          u"orderno"]
    # ## delete validateion
    # def validate(self, extra_validators=None):
    #     import sqlalchemy.orm as orm
    #     super(CategoryForm, self).validate(extra_validators=extra_validators)

    #     data = self.data
    #     parent = orm.aliased(Category, name="parent")
    #     if Category.query.filter(Category.parent_id==parent.id).filter(
    #         parent.name==data["name"], 
    #         parent.label==data["label"], 
    #         ).count() > 0:
    #         self.warns["hierarchy"] = u"まだ子を持ったカテゴリを消そうとしています"
    ## site


def as_filter(kwargs):
    def wrapper(self, qs):
        for k in kwargs:
            it = self.data.get(k)
            if it and "__None" != it:
                qs = qs.filter_by(**{k: it})
        return qs
    return wrapper


class CategoryFilterForm(Form):
    hierarchy = fields.SelectField(label=u"階層", choices=[("__None", "----------")]+[(x, x) for x in [u"大", u"中", u"小"]])
    parent = dynamic_query_select_field_factory(
        Category, allow_blank=True, blank_text=u"----------", label=u"親カテゴリ",
        get_label=lambda obj: obj.label or u"---名前なし---")

    as_filter = as_filter(["hierarchy", "parent"])


class TopicForm(Form):
    title = fields.TextField(label=u"タイトル", validators=[required_field()])
    kind = fields.SelectField(label=u"トピックの種別", 
                              choices=[(x, x) for x in Topic.KIND_CANDIDATES],
                              validators=[required_field()])
    subkind = fields.TextField(label=u"サブ分類")
    is_global = fields.BooleanField(label=u"全体に公開", default=True)
    text = fields.TextField(label=u"内容", validators=[required_field()], widget=widgets.TextArea())

    publish_open_on = fields.DateTimeField(label=u"公開開始日", validators=[required_field()])
    publish_close_on = fields.DateTimeField(label=u"公開終了日", validators=[required_field()])
    
    orderno = fields.IntegerField(label=u"表示順序(1〜100)", default=50)
    is_vetoed = fields.BooleanField(label=u"公開禁止")

    bound_page = dynamic_query_select_field_factory(PageSet, 
                                                    label=u"表示ページ",
                                                    query_factory=lambda : PageSet.query.filter(PageSet.event_id==None), 
                                                    allow_blank=True, 
                                                    get_label=lambda obj: obj.name or u"名前なし")
    linked_page = dynamic_query_select_field_factory(PageSet, 
                                                     label=u"リンク先ページ",
                                                     query_factory=lambda : PageSet.query, 
                                                     allow_blank=True, 
                                                     get_label=lambda obj: obj.name or u"名前なし")
    event = dynamic_query_select_field_factory(Event, 
                                               label=u"関連イベント",
                                               allow_blank=True, 
                                               get_label=lambda obj: obj.title or u"名前なし")

    __display_fields__ = [u"title", u"kind", u"subkind", u"is_global", 
                          u"text", 
                          u"publish_open_on", u"publish_close_on", 
                          u"orderno", u"is_vetoed", 
                          u"bound_page", u"linked_page", u"event"]

class TopicFilterForm(Form):
    kind = fields.SelectField(label=u"トピックの種類", choices=[("__None", "----------")]+[(x, x) for x in Topic.KIND_CANDIDATES])
    subkind = fields.TextField(label=u"サブ分類")    

    as_filter = as_filter(["kind", "subkind"])


class TopcontentForm(Form):
    title = fields.TextField(label=u"タイトル", validators=[required_field()])
    kind = fields.SelectField(label=u"種別", choices=[(x, x) for x in Topcontent.KIND_CANDIDATES])
    subkind = fields.TextField(label=u"サブ分類")
    is_global = fields.BooleanField(label=u"全体に公開", default=True)

    text = fields.TextField(label=u"内容", validators=[required_field()], widget=widgets.TextArea())
    countdown_type = fields.SelectField(label=u"カウントダウンの種別", choices=Topcontent.COUNTDOWN_CANDIDATES)    
    image_asset = dynamic_query_select_field_factory(ImageAsset,label=u"画像", allow_blank=True)

    publish_open_on = fields.DateTimeField(label=u"公開開始日", validators=[required_field()])
    publish_close_on = fields.DateTimeField(label=u"公開終了日", validators=[required_field()])

    
    orderno = fields.IntegerField(label=u"表示順序(1〜100)", default=50)
    is_vetoed = fields.BooleanField(label=u"公開禁止")

    ##本当は、client.id, site.idでfilteringする必要がある
    bound_page = dynamic_query_select_field_factory(PageSet, 
                                                    label=u"表示ページ",
                                                    query_factory=lambda : PageSet.query.filter(PageSet.event_id==None), 
                                                    allow_blank=True, 
                                                    get_label=lambda obj: obj.name or u"名前なし")
    linked_page = dynamic_query_select_field_factory(PageSet, 
                                                     label=u"リンク先ページ",
                                                     query_factory=lambda : PageSet.query, 
                                                     allow_blank=True, 
                                                     get_label=lambda obj: obj.name or u"名前なし")

    __display_fields__= [u"title", u"kind", u"subkind", u"is_global", 
                         u"text", u"countdown_type", u"image_asset", 
                         u"publish_open_on", u"publish_close_on", 
                         u"orderno", u"is_vetoed", 
                         u"bound_page", u"linked_page"]
    
   

class HotWordForm(Form):
    name = fields.TextField(label=u"ホットワード名")
    tag = dynamic_query_select_field_factory(PageTag, label=u"検索用ページタグ", allow_blank=True, 
                                                 get_label=lambda obj: obj.label or u"名前なし")
    enablep = fields.BooleanField(label=u"利用する/しない")
    term_begin = fields.DateTimeField(label=u"利用開始日", validators=[required_field()])
    term_end = fields.DateTimeField(label=u"利用終了日", validators=[required_field()])
    orderno = fields.IntegerField(label=u"表示順序")
    
    
    __display_fields__ = [u"name", u"tag",
                          u"enablep", u"term_begin", u"term_end", 
                          u"orderno"]
