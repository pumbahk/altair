# -*- coding:utf-8 -*-
import logging 
logger = logging.getLogger(__name__)
import json
from altaircms.formhelpers import Form, MaybeSelectField
from wtforms import fields
from wtforms import widgets
from wtforms import validators
import sqlalchemy.orm as orm
import wtforms.ext.sqlalchemy.fields as extfields
import urllib

from altaircms.formhelpers import dynamic_query_select_field_factory
from altaircms.formhelpers import required_field, append_errors


from ..event.models import Event
from altaircms.models import Performance, Genre
from ..models import Category, SalesSegment, SalesSegmentGroup
from ..asset.models import ImageAsset
from ..page.models import PageSet, MobileTag
from ..topic.models import TopicTag, Topcontent,TopcontentTag, PromotionTag, Promotion
from ..page.models import PageTag, PageType
from ..plugins.api import get_extra_resource
from ..helpers.event import performance_name

import pkg_resources
def import_symbol(symbol):
    return pkg_resources.EntryPoint.parse("x=%s" % symbol).load(False)


def quote(x):
    return urllib.quote(x.encode("utf-8"), safe="%/:=&?~#+!$,;'@()*[]").decode("utf-8") if x else None

def pageset_label(pageset):
    if pageset is None:
        u"-----"
    else:
        return u"{1} (url:{0})".format(pageset.url, pageset.name)

class TermValidator(object):
    def __init__(self, begin, end, message):
        self.begin = begin
        self.end = end
        self.message = message

    def __call__(self, data, errors):
        if data[self.end] and data[self.begin] and data[self.begin] > data[self.end]:
            append_errors(errors, self.begin, self.message)

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

class LayoutCreateForm(Form):
    title = fields.TextField(u'タイトル', validators=[validators.Required()])
    template_filename = fields.TextField(u'テンプレートファイル名', validators=[validators.Required()])
    filepath = fields.FileField(label=u"テンプレートファイル")
    __display_fields__ = [u"title", "template_filename", "filepath"]

class LayoutUpdateForm(Form):
    title = fields.TextField(u'タイトル', validators=[validators.Required()])
    blocks = fields.TextField(u'ブロック', validators=[validators.Required(), validate_blocks])
    template_filename = fields.TextField(u'テンプレートファイル名', validators=[validators.Optional()])
    filepath = fields.FileField(label=u"テンプレートファイル", validators=[validators.Optional()])
    __display_fields__ = [u"title", "template_filename", "filepath", "blocks"]

class PerformanceForm(Form):
    title = fields.TextField(label=u"公演タイトル")
    backend_id = fields.IntegerField(validators=[required_field()], label=u"バックエンド管理番号")
    event = dynamic_query_select_field_factory(Event, allow_blank=False, label=u"イベント", get_label=lambda obj: obj.title)
    prefecture = fields.SelectField(label=u"開催県", choices=import_symbol("altaircms.seeds.prefecture:PREFECTURE_CHOICES"))
    venue = fields.TextField(label=u"開催場所(詳細)")
    open_on = fields.DateTimeField(label=u"開場時間", validators=[validators.Optional()])
    start_on = fields.DateTimeField(label=u"開始時間", validators=[required_field()])
    end_on = fields.DateTimeField(label=u"終了時間", validators=[validators.Optional()])

    purchase_link = fields.TextField(label=u"購入ページリンク", filters=[quote])
    mobile_purchase_link = fields.TextField(label=u"購入ページリンク(mobile)", filters=[quote])
    calendar_content = fields.TextField(label=u"カレンダーに追加する文字列")

    def validate(self, **kwargs):
        if super(PerformanceForm, self).validate():
            data = self.data
            try:
                if data["open_on"] and data["start_on"] is None:
                    data["start_on"] = data["open_on"]

                if data["end_on"] and data["start_on"]:
                    if not (data["open_on"] <= data["start_on"] <= data["end_on"]):
                        append_errors(self.errors, "open_on", u"開場時間、開始時間、終了時間の順になっていません")
                    
            except Exception, e:
                logger.debug(str(e))
                append_errors(self.errors, "__all__", u"不正な文字列が入力されてます。")
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

validate_term = TermValidator("start_on", "end_on",  u"公開開始日よりも後に終了日が設定されています")
class SalesSegmentForm(Form):
    performance = dynamic_query_select_field_factory(Performance,
                                                     dynamic_query=lambda model, request, query: query.filter_by(id=request.params["performance_id"]), 
                                                     allow_blank=False, label=u"パフォーマンス", get_label=lambda obj: performance_name(obj))
    group = dynamic_query_select_field_factory(SalesSegmentGroup, 
                                               dynamic_query=lambda model, request, query: query.filter(SalesSegmentGroup.event_id==Performance.event_id, Performance.id==request.params["performance_id"]), 
                                               allow_blank=False, label=u"販売区分名", get_label=lambda obj: obj.name)
    start_on = fields.DateTimeField(label=u"開始時間",validators=[])
    end_on = fields.DateTimeField(label=u"終了時間",validators=[])
       
    __display_fields__ = [u"performance", u"group", u"start_on", u"end_on"]

    def validate(self, **kwargs):
        if super(SalesSegmentForm, self).validate():
            validate_term(self.data, self.errors)
            # data = self.data
            # if not data["name"]:
            #     data["name"] = data["event"].title
        return not bool(self.errors)


class TicketForm(Form):
    sale = dynamic_query_select_field_factory(SalesSegment, 
                                              allow_blank=False,
                                              label=u"販売区分", 
                                              dynamic_query=lambda model, request, query: query.filter_by(id=request.params["salessegment_id"]).options(orm.joinedload(SalesSegment.group)), 
                                              get_label=lambda obj: obj.group.name if obj.group else u"---")
    name = fields.TextField(validators=[required_field()], label=u"商品名")
    seattype = fields.TextField(validators=[], label=u"席種／グレード")
    price = fields.IntegerField(validators=[required_field()], label=u"料金")
    # display_order = fields.TextField(label=u"表示順序(default:50)")
    def validate_display_order(form, field):
        if not field.data:
            field.data = "50"

    __display_fields__ = [u"sale", u"seattype", u"name", u"price"]
    # __display_fields__ = [u"sale", u"name", u"seattype", u"price", u"display_order"]

validate_publish_term = TermValidator("publish_open_on", "publish_close_on",  u"公開開始日よりも後に終了日が設定されています")
class TopicForm(Form):
    title = fields.TextField(label=u"タイトル", validators=[required_field()])
    tag_content = fields.SelectMultipleField(label=u"種別", choices=[]) #@todo rename
    genre = fields.SelectMultipleField(label=u"ジャンル", coerce=unicode)
    text = fields.TextField(label=u"内容", validators=[required_field()], widget=widgets.TextArea())
    publish_open_on = fields.DateTimeField(label=u"公開開始日", validators=[required_field()])
    publish_close_on = fields.DateTimeField(label=u"公開終了日", validators=[validators.Optional()])


    linked_page = dynamic_query_select_field_factory(PageSet, allow_blank=True,label=u"リンク先ページ(CMSで作成したもの)", 
                                                     query_factory=lambda : PageSet.query.order_by("name"), 
                                                     get_label=pageset_label)
    link = fields.TextField(label=u"外部リンク(ページより優先)", filters=[quote])
    mobile_link = fields.TextField(label=u"mobile外部リンク(ページより優先)", filters=[quote])
    mobile_tag = dynamic_query_select_field_factory(MobileTag, label=u"モバイル検索用ページタグ", allow_blank=True, get_label=lambda obj: obj.label or u"名前なし")

    display_order = fields.IntegerField(label=u"表示順序(1〜100)", default=50)
    is_vetoed = fields.BooleanField(label=u"公開禁止")
    __display_fields__= [u"title", u"tag_content", u"genre", 
                         u"text",
                         u"publish_open_on", u"publish_close_on", 
                         u"display_order", u"is_vetoed", 
                         u"linked_page", u"link", u"mobile_link", u"mobile_tag"]
    
    def validate(self, **kwargs):
        if super(TopicForm, self).validate():
            validate_publish_term(self.data, self.errors)
        return not bool(self.errors)

    def configure(self, request):
        self.tag_content.choices = [(t.label, t.label) for t in request.allowable(TopicTag).filter_by(publicp=True)]
        self.genre.choices = [(unicode(g.id), g.label) for g in request.allowable(Genre)]

class TopcontentForm(Form):
    title = fields.TextField(label=u"タイトル", validators=[required_field()])
    tag_content = fields.SelectMultipleField(label=u"種別", choices=[])
    genre = fields.SelectMultipleField(label=u"ジャンル", coerce=unicode)
    countdown_type = fields.SelectField(label=u"カウントダウンの種別", choices=Topcontent.COUNTDOWN_CANDIDATES)    
    text = fields.TextField(label=u"内容", validators=[required_field()], widget=widgets.TextArea())
    image_asset = dynamic_query_select_field_factory(ImageAsset,label=u"画像", allow_blank=True, 
                                                     get_label=lambda o: o.title)
    mobile_image_asset = dynamic_query_select_field_factory(ImageAsset,label=u"mobile画像", allow_blank=True, 
                                                            get_label=lambda o: o.title)

    publish_open_on = fields.DateTimeField(label=u"公開開始日", validators=[required_field()])
    publish_close_on = fields.DateTimeField(label=u"公開終了日", validators=[validators.Optional()])


    linked_page = dynamic_query_select_field_factory(PageSet, allow_blank=True,label=u"リンク先ページ(CMSで作成したもの)", 
                                                     query_factory=lambda : PageSet.query.order_by("name"), 
                                                     get_label=pageset_label)
    link = fields.TextField(label=u"外部リンク(ページより優先)", filters=[quote])
    mobile_link = fields.TextField(label=u"mobile外部リンク(ページより優先)", filters=[quote])
    mobile_tag = dynamic_query_select_field_factory(MobileTag, label=u"モバイル検索用ページタグ", allow_blank=True, get_label=lambda obj: obj.label or u"名前なし")

    display_order = fields.IntegerField(label=u"表示順序(1〜100)", default=50)
    is_vetoed = fields.BooleanField(label=u"公開禁止")

    __display_fields__= [u"title", u"tag_content", u"genre", 
                         u"text", u"countdown_type", u"image_asset",u"mobile_image_asset",  
                         u"publish_open_on", u"publish_close_on", 
                         u"display_order", u"is_vetoed", 
                         u"linked_page", u"link", u"mobile_link", u"mobile_tag"]
    
    def validate(self, **kwargs):
        if super(TopcontentForm, self).validate():
            validate_publish_term(self.data, self.errors)
        return not bool(self.errors)
   
    def configure(self, request):
        self.tag_content.choices = [(t.label, t.label) for t in request.allowable(TopcontentTag).filter_by(publicp=True)]
        self.genre.choices = [(unicode(g.id), g.label) for g in request.allowable(Genre)]

class PromotionForm(Form):
    tag_content = fields.SelectMultipleField(label=u"表示場所", choices=[]) #@todo rename
    genre = fields.SelectMultipleField(label=u"ジャンル", coerce=unicode)
    main_image = dynamic_query_select_field_factory(
        ImageAsset, allow_blank=False, label=u"メイン画像",
        get_label=lambda obj: obj.title or u"名前なし")
    text = fields.TextField(validators=[required_field()], label=u"画像下のメッセージ")
    linked_page = dynamic_query_select_field_factory(
        PageSet, allow_blank=True, label=u"リンク先ページ(CMSで作成したもの)",
        query_factory=lambda : PageSet.query.order_by("name"), 
        get_label=pageset_label)
    link = fields.TextField(label=u"外部リンク(ページより優先)", filters=[quote])
    mobile_tag = dynamic_query_select_field_factory(MobileTag, label=u"モバイル検索用ページタグ", allow_blank=True, get_label=lambda obj: obj.label or u"名前なし")
    publish_open_on = fields.DateTimeField(label=u"公開開始日", validators=[required_field()])
    publish_close_on = fields.DateTimeField(label=u"公開終了日", validators=[required_field()])
    
    display_order = fields.IntegerField(label=u"表示順序(1〜100)", default=50)
    is_vetoed = fields.BooleanField(label=u"公開禁止")

    def validate(self, **kwargs):
        if super(PromotionForm, self).validate():
            validate_publish_term(self.data, self.errors)
        return not bool(self.errors)

    __display_fields__ = [
        u"tag_content", u"genre", 
        u"main_image", u"text", u"linked_page", u"link", u"mobile_tag",
        u"publish_open_on", u"publish_close_on", u"display_order", u"is_vetoed"
        ]

    def configure(self, request):
        self.tag_content.choices = [(t.label, t.label) for t in request.allowable(PromotionTag).filter_by(publicp=True)]
        self.genre.choices = [(unicode(g.id), g.label) for g in request.allowable(Genre)]

class PromotionFilterForm(Form):
    tag = dynamic_query_select_field_factory(
        PromotionTag, allow_blank=False, label=u"表示場所",
        get_label=lambda obj: obj.name)

    def as_filter(self, qs):
        tag = self.data.get("tag")
        if tag and "__None" != tag:
            qs = qs.filter(Promotion.tags.any(PromotionTag.name==tag.name))
        return qs

class CategoryForm(Form):
    name = fields.TextField(label=u"カテゴリ名")
    origin = fields.TextField(label=u"分類")
    label = fields.TextField(label=u"label")
    attributes = fields.TextField(label=u"attributes")
    parent = dynamic_query_select_field_factory(
        Category, allow_blank=True, blank_text=u"--------", label=u"親カテゴリ",
        get_label=lambda obj: obj.label or u"--なし--")

    pageset = dynamic_query_select_field_factory(
        PageSet, allow_blank=True, blank_text=u"--------", label=u"リンク先ページ(CMSで作成したもの)",
        get_label=pageset_label)
    hierarchy = fields.SelectField(label=u"表示場所", choices=[])
    # hierarchy = fields.SelectField(label=u"階層")
    imgsrc = fields.TextField(label=u"imgsrc(e.g. /static/ticketstar/img/common/header_nav_top.gif)")
    url = fields.TextField(label=u"リンク(外部ページのURL)")
    display_order = fields.IntegerField(label=u"表示順序")

    __display_fields__ = [u"name", u"origin", u"label", u"attributes", 
                          u"parent", u"hierarchy", 
                          u"imgsrc", u"url", u"pageset", 
                          u"display_order"]
    def configure(self, request):
        extra_resource = get_extra_resource(request)
        self.hierarchy.choices = [(x, x) for x in extra_resource["category_kinds"]]
        
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


class ExternalLinkForm(Form):
    label = fields.TextField(label=u"ページ上の表記")
    attributes = fields.TextField(label=u"attributes")
    pageset = dynamic_query_select_field_factory(
        PageSet, allow_blank=True, blank_text=u"--------", label=u"リンク(CMSで作成したもの)",
        get_label=pageset_label)
    hierarchy = fields.SelectField(label=u"表示場所", choices=[])
    url = fields.TextField(label=u"リンク(外部ページのURL)")
    display_order = fields.IntegerField(label=u"表示順序")

    def configure(self, request):
        extra_resource = get_extra_resource(request)
        self.hierarchy.choices = [(x, x) for x in extra_resource["category_kinds"]]

    __display_fields__ = [u"hierarchy", 
                          u"label",u"attributes", 
                          u"url", u"pageset", 
                          u"display_order"]

class ExternalBannerForm(Form):
    label = fields.TextField(label=u"バナー画像の説明文")
    attributes = fields.TextField(label=u"attributes")
    pageset = dynamic_query_select_field_factory(
        PageSet, allow_blank=True, blank_text=u"--------", label=u"リンク(CMSで作成したもの)",
        get_label=pageset_label)
    hierarchy = fields.SelectField(label=u"階層", choices=[])
    imgsrc = fields.TextField(label=u"imgsrc(e.g. /static/ticketstar/img/common/header_nav_top.gif)")
    url = fields.TextField(label=u"リンク(外部ページのURL)")
    display_order = fields.IntegerField(label=u"表示順序")

    def configure(self, request):
        extra_resource = get_extra_resource(request)
        self.hierarchy.choices = [(x, x) for x in extra_resource["category_kinds"]]

    __display_fields__ = [u"hierarchy", 
                          u"label", u"attributes", u"imgsrc", 
                          u"url", u"pageset", 
                          u"display_order"]

class TopicFilterForm(Form):
    kind = fields.SelectField(label=u"トピックの種類", choices=[])
    subkind = fields.TextField(label=u"サブ分類")    

    as_filter = as_filter(["kind", "subkind"])

    def configure(self, request):
        extra_resource = get_extra_resource(request)
        self.kind.choices = [("__None", "----------")]+[(x, x) for x in extra_resource["topic_kinds"]]

class HotWordForm(Form):
    name = fields.TextField(label=u"ホットワード名")
    tag = dynamic_query_select_field_factory(PageTag, label=u"検索用ページタグ", allow_blank=True, 
                                                 get_label=lambda obj: obj.label or u"名前なし")
    enablep = fields.BooleanField(label=u"利用する/しない")
    term_begin = fields.DateTimeField(label=u"利用開始日", validators=[required_field()])
    term_end = fields.DateTimeField(label=u"利用終了日", validators=[required_field()])
    display_order = fields.IntegerField(label=u"表示順序")
    
    
    __display_fields__ = [u"name", u"tag",
                          u"enablep", u"term_begin", u"term_end", 
                          u"display_order"]

    def validate(self, **kwargs):
        if super(HotWordForm, self).validate():
            data = self.data
            if data["term_begin"] and data["term_end"] and data["term_begin"] > data["term_end"]:
                append_errors(self.errors, "term_begin", u"開始日よりも後に終了日が設定されています")
        return not bool(self.errors)

class PageDefaultInfoForm(Form):
    url_prefix = fields.TextField(label=u"urlのフォーマット", validators=[])    
    title_prefix = fields.TextField(label=u"titleのフォーマット", validators=[])    
    description = fields.TextField(label=u"descriptionのデフォルト値",  widget=widgets.TextArea())    
    keywords = fields.TextField(label=u"keywordsのデフォルト値",  widget=widgets.TextArea())    
    pagetype = dynamic_query_select_field_factory(PageType, 
                                                  label=u"ページタイプ", 
                                                  get_label=lambda obj: obj.label)
    __display_fields__ = ["pagetype", "title_prefix", "url_prefix", "keywords", "description"]

class PageTypeForm(Form):
    name = fields.TextField(label=u"名前", validators=[required_field()])
    label = fields.TextField(label=u"日本語表記", validators=[required_field()])
    page_role = MaybeSelectField(choices=PageType.page_role_candidates, label=u"ページの利用方法")
    page_rendering_type = fields.SelectField(choices=PageType.page_rendering_type_candidates, label=u"ページのレンダリング方法")

    def validate_page_role(field, data):
        if data is None:
            field.data = PageType.page_default_role
    __display_fields__ = ["name", "label", "page_role", "page_rendering_type"]

class PageSetForm(Form):
    name = fields.TextField(label=u"名前")
    tags_string = fields.TextField(label=u"タグ(区切り文字:\",\")")
    private_tags_string = fields.TextField(label=u"非公開タグ(区切り文字:\",\")")
    mobile_tags_string = fields.TextField(label=u"モバイル用タグ(区切り文字:\",\")")
    genre_id = fields.SelectField(label=u"ジャンル", coerce=unicode)
    url = fields.TextField(label=u"URL")

    def configure(self, request):
        self.genre_id.choices = [(unicode(g.id), unicode(g)) for g in request.allowable(Genre)]
    __display_fields__ = ["name", "genre_id", "url", "tags_string", "private_tags_string", "mobile_tags_string"]
