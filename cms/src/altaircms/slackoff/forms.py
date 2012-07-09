# -*- coding:utf-8 -*-

import json
from wtforms.form import Form
from wtforms import fields
from wtforms import widgets
from wtforms import validators
import wtforms.ext.sqlalchemy.fields as extfields


from altaircms.lib.formhelpers import dynamic_query_select_field_factory
from altaircms.helpers.formhelpers import required_field, append_errors


from ..event.models import Event
from altaircms.models import Performance
from ..plugins.widget.promotion.models import Promotion
from ..models import Category, Sale
from ..asset.models import ImageAsset
from ..page.models import PageSet
from ..topic.models import Topic, Topcontent
from ..tag.models import PageTag


import pkg_resources
def import_symbol(symbol):
    return pkg_resources.EntryPoint.parse("x=%s" % symbol).load(False)


"""
class ISlackOffForm(Interface):
    __display_fields__ = Attribute("display fields")
    def configure(request):
        pass
    def object_validate(obj=None):
        pass
"""

def as_filter(kwargs):
    def wrapper(self, qs):
        for k in kwargs:
            it = self.data.get(k)
            if it and "__None" != it:
                qs = qs.filter_by(**{k: it})
        return qs
    return wrapper

def validate_blocks(form, field):
    ## + complete json
    ## + elements of field.data is list like object
    try:
        if not all(hasattr(x, "__iter__") for x in json.loads(field.data)):
            raise ValueError("")
    except ValueError:
        raise validators.ValidationError(u'正しいjson形式で入力してください(e.g. [["top"], ["left", "right"], ["bottom"]]) ')

class LayoutForm(Form):
    title = fields.TextField(u'タイトル', validators=[validators.Required()])
    template_filename = fields.TextField(u'テンプレートファイル名', validators=[validators.Required()])
    blocks = fields.TextField(u'ブロック', validators=[validators.Required(), validate_blocks])

    __display_fields__ = [u"title", u"template_filename", u"blocks"]

    def validate_template_filename(form, field):
        pass
    
class PerformanceForm(Form):
    title = fields.TextField(label=u"公演タイトル")
    backend_id = fields.IntegerField(validators=[required_field()], label=u"バックエンド管理番号")
    event = dynamic_query_select_field_factory(Event, allow_blank=False, label=u"イベント", get_label=lambda obj: obj.title)
    prefecture = fields.SelectField(label=u"開催県", choices=import_symbol("altaircms.seeds.prefecture:PREFECTURE_CHOICES"))
    venue = fields.TextField(label=u"開催場所(詳細)")
    open_on = fields.DateTimeField(label=u"開場時間", validators=[required_field()])
    start_on = fields.DateTimeField(label=u"開始時間", validators=[required_field()])
    end_on = fields.DateTimeField(label=u"終了時間", validators=[])

    purchase_link = fields.TextField(label=u"購入ページリンク")
    mobile_purchase_link = fields.TextField(label=u"購入ページリンク(mobile)")
    calendar_content = fields.TextField(label=u"カレンダーに追加する文字列")

    def validate(self, **kwargs):
        data = self.data
        if data["open_on"] and data["start_on"] is None:
            data["start_ono"] = data["open_on"]
        elif data["start_on"] and data["open_on"] is None:
            data["open_ono"] = data["start_on"]

        if data["open_on"] > data["start_on"]:
            append_errors(self.errors, "open_on", u"開始時刻よりも後に開場時刻が設定されてます")
        if data["end_on"] and data["start_on"] > data["end_on"]:
            append_errors(self.errors, "open_on", u"終了時刻よりも後に開始時刻が設定されてます")
        return not bool(self.errors)

    def object_validate(self, obj=None):
        data = self.data
        qs = Performance.query.filter(Performance.backend_id == data["backend_id"])
        if obj:
            qs = qs.filter(Performance.backend_id != obj.backend_id)
        if qs.count() >= 1:
            append_errors(self.errors, "backend_id", u"バックエンドIDが重複しています。(%s)" % data["backend_id"])
        return not bool(self.errors)

    __display_fields__ = [u"title", u"backend_id", u"event",
                          u"prefecture", u"venue", 
                          u"open_on", u"start_on", u"end_on",
                          u"purchase_link", u"mobile_purchase_link", 
                          u"calendar_content"]


class SaleForm(Form):
    event = dynamic_query_select_field_factory(Event, allow_blank=False, label=u"イベント", get_label=lambda obj: obj.title) ## performance?
    kind = fields.SelectField(label=u"販売条件", choices=import_symbol("altaircms.seeds.saleskind:SALESKIND_CHOICES"))
    name = fields.TextField(label=u"名前", validators=[required_field()])
    start_on = fields.DateTimeField(label=u"開始時間（省略可)")
    end_on = fields.DateTimeField(label=u"終了時間(省略可)")
       
    __display_fields__ = [u"event", u"kind", u"name", u"start_on", u"end_on"]

    def validate(self, **kwargs):
        data = self.data
        if not data["name"]:
            data["name"] = data["event"].title
        return not bool(self.errors)


class TicketForm(Form):
    # event = dynamic_query_select_field_factory(Event, allow_blank=False, label=u"イベント", get_label=lambda obj: obj.title) ## performance?
    sale = dynamic_query_select_field_factory(Sale, 
                                              allow_blank=False,
                                              label=u"イベント販売条件", 
                                              get_label=lambda obj: obj.name) ## performance?
    name = fields.TextField(validators=[required_field()], label=u"券種")
    seattype = fields.TextField(validators=[], label=u"席種／グレード")
    price = fields.IntegerField(validators=[required_field()], label=u"料金")
    # orderno = fields.TextField(label=u"表示順序(default:50)")
    def validate_orderno(form, field):
        if not field.data:
            field.data = "50"

    __display_fields__ = [u"sale",u"name",  u"seattype", u"price"]
    # __display_fields__ = [u"sale", u"name", u"seattype", u"price", u"orderno"]

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

    pageset = dynamic_query_select_field_factory(
        PageSet, allow_blank=True, label=u"リンク先ページ(CMSで作成したもの)",
        get_label=lambda obj: obj.name or u"--なし--")
    link = fields.TextField(label=u"外部リンク(ページより優先)")
    __display_fields__ = [u"promotion", u"main_image", u"text", u"thumbnail", "pageset", "link"]
    

class PromotionUnitFilterForm(Form):
    promotion = extfields.QuerySelectField(id="promotion", label=u"プロモーション枠", 
                                           get_label=lambda obj: obj.name, 
                                           query_factory = lambda : Promotion.query)
    as_filter = as_filter(["promotion"])

class PromotionForm(Form):
    name = fields.TextField(label=u"プロモーション枠名")
    ## organization
    __display_fields__ = [u"name"]

_hierarchy_choices = [(x, x) for x in [u"大", u"中", u"小", "top_couter", "top_inner", "masked"]]
class CategoryForm(Form):
    name = fields.TextField(label=u"カテゴリ名")
    origin = fields.TextField(label=u"分類")
    label = fields.TextField(label=u"label")
    parent = dynamic_query_select_field_factory(
        Category, allow_blank=False, label=u"親カテゴリ",
        get_label=lambda obj: obj.label or u"--なし--")

    pageset = dynamic_query_select_field_factory(
        PageSet, allow_blank=False, label=u"リンク先ページ(CMSで作成したもの)",
        get_label=lambda obj: obj.name or u"--なし--")
    hierarchy = fields.SelectField(label=u"階層", choices=_hierarchy_choices)
    # hierarchy = fields.SelectField(label=u"階層")
    imgsrc = fields.TextField(label=u"imgsrc(e.g. /static/ticketstar/img/common/header_nav_top.gif)")
    url = fields.TextField(label=u"リンク(外部ページのURL)")
    pageset = dynamic_query_select_field_factory(
        PageSet, allow_blank=False, label=u"リンク先ページ(CMSで作成したもの)",
        get_label=lambda obj: obj.name or u"--なし--")
    orderno = fields.IntegerField(label=u"表示順序")

    __display_fields__ = [u"name", u"origin", u"label",
                          u"parent", u"hierarchy", 
                          u"imgsrc", u"url", u"pageset", 
                          u"orderno"]

    # def configure(self, request):
    #     qs = DBSession.query(Category.hierarchy)
    #     if hasattr(request, "organization"):
    #         qs = qs.filter_by(organization=request.organization)
    #     self.hierarchy.choices = qs

    # ## delete validateion
    # def object_validate(self, obj=None):
    #     import sqlalchemy.orm as orm
    #     super(CategoryForm, self).validate(extra_validators=extra_validators)

    #     data = self.data
    #     parent = orm.aliased(Category, name="parent")
    #     if Category.query.filter(Category.parent_id==parent.id).filter(
    #         parent.name==data["name"], 
    #         parent.label==data["label"], 
    #         ).count() > 0:
    #         self.warns["hierarchy"] = u"まだ子を持ったカテゴリを消そうとしています"
    ## organization


class CategoryFilterForm(Form):
    hierarchy = fields.SelectField(label=u"階層", choices=[("__None", "----------")]+_hierarchy_choices)
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
                                                    # query_factory=lambda : PageSet.query.order_by("name").filter(PageSet.event_id==None), 
                                                    query_factory=lambda : PageSet.query.order_by("name"), 
                                                    allow_blank=True, 
                                                    get_label=lambda obj: obj.name or u"名前なし")
    linked_page = dynamic_query_select_field_factory(PageSet, 
                                                     label=u"リンク先ページ",
                                                     query_factory=lambda : PageSet.query.order_by("name"), 
                                                     allow_blank=True, 
                                                     get_label=lambda obj: obj.name or u"名前なし")
    link = fields.TextField(label=u"外部リンク(ページより優先)")
    mobile_link = fields.TextField(label=u"外部リンク(mobile ページより優先)")
    event = dynamic_query_select_field_factory(Event, 
                                               label=u"関連イベント",
                                               allow_blank=True, 
                                               get_label=lambda obj: obj.title or u"名前なし")

    __display_fields__ = [u"title", u"kind", u"subkind", u"is_global", 
                          u"text", 
                          u"publish_open_on", u"publish_close_on", 
                          u"orderno", u"is_vetoed", 
                          u"bound_page", u"linked_page", u"link", u"mobile_link", u"event"]

    def validate(self, **kwargs):
        data = self.data
        if data["publish_open_on"] > data["publish_close_on"]:
            append_errors(self.errors, "publish_open_on", u"公開開始日よりも後に終了日が設定されています")
        return not bool(self.errors)

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
    image_asset = dynamic_query_select_field_factory(ImageAsset,label=u"画像", allow_blank=True, 
                                                     get_label=lambda o: o.title)
    mobile_image_asset = dynamic_query_select_field_factory(ImageAsset,label=u"mobile画像", allow_blank=True, 
                                                            get_label=lambda o: o.title)

    publish_open_on = fields.DateTimeField(label=u"公開開始日", validators=[required_field()])
    publish_close_on = fields.DateTimeField(label=u"公開終了日", validators=[required_field()])

    
    orderno = fields.IntegerField(label=u"表示順序(1〜100)", default=50)
    is_vetoed = fields.BooleanField(label=u"公開禁止")

    ##本当は、client.id, organization.idでfilteringする必要がある
    bound_page = dynamic_query_select_field_factory(PageSet, 
                                                    label=u"表示ページ",
                                                    query_factory=lambda : PageSet.query.order_by("name").filter(PageSet.event_id==None), 
                                                    allow_blank=True, 
                                                    get_label=lambda obj: obj.name or u"名前なし")
    linked_page = dynamic_query_select_field_factory(PageSet, 
                                                     label=u"リンク先ページ",
                                                     query_factory=lambda : PageSet.query.order_by("name"), 
                                                     allow_blank=True, 
                                                     get_label=lambda obj: obj.name or u"名前なし")
    link = fields.TextField(label=u"外部リンク(ページより優先)")
    mobile_link = fields.TextField(label=u"外部リンク(mobile ページより優先)")

    __display_fields__= [u"title", u"kind", u"subkind", u"is_global", 
                         u"text", u"countdown_type", u"image_asset",u"mobile_image_asset",  
                         u"publish_open_on", u"publish_close_on", 
                         u"orderno", u"is_vetoed", 
                         u"bound_page", u"linked_page", u"link", u"mobile_link"]
    
    def validate(self, **kwargs):
        data = self.data
        if data["publish_open_on"] > data["publish_close_on"]:
            append_errors(self.errors, "publish_open_on", u"公開開始日よりも後に終了日が設定されています")
        return not bool(self.errors)
   

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

    def validate(self, **kwargs):
        data = self.data
        if data["term_begin"] > data["term_end"]:
            append_errors(self.errors, "term_begin", u"開始日よりも後に終了日が設定されています")
        return not bool(self.errors)

class PageDefaultInfoForm(Form):
    url_fmt = fields.TextField(label=u"urlのフォーマット", validators=[required_field()], widget=widgets.TextArea())    
    title_fmt = fields.TextField(label=u"titleのフォーマット", validators=[required_field()], widget=widgets.TextArea())    
    description = fields.TextField(label=u"descriptionのデフォルト値",  widget=widgets.TextArea())    
    keywords = fields.TextField(label=u"keywordsのデフォルト値",  widget=widgets.TextArea())    
    pageset = dynamic_query_select_field_factory(PageSet, 
                                                     label=u"親となるページセット",
                                                     query_factory=lambda : PageSet.query.order_by("name"), 
                                                     allow_blank=True, 
                                                     get_label=lambda obj: obj.name or u"名前なし")

    __display_fields__ = ["pageset", "title_fmt", "url_fmt", "keywords", "description"]
