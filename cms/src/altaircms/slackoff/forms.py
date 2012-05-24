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
from ..page.models import PageSet, Page
from ..topic.models import Topic
from ..topcontent.models import Topcontent


import pkg_resources
def import_symbol(symbol):
    return pkg_resources.EntryPoint.parse("x=%s" % symbol).load(False)


class LayoutForm(Form):
    title = fields.TextField(u'タイトル', validators=[validators.Required()])
    blocks = fields.TextField(u'ブロック', validators=[validators.Required()])
    template_filename = fields.TextField(u'テンプレートファイル名', validators=[validators.Required()])

    
class PerformanceForm(Form):
    backend_id = fields.IntegerField(validators=[required_field()], label=u"バックエンド管理番号")
    event = dynamic_query_select_field_factory(Event, allow_blank=False, label=u"イベント", get_label=lambda obj: obj.title)
    title = fields.TextField(label=u"講演タイトル")
    prefecture = fields.SelectField(label=u"開催県", choices=import_symbol("altaircms.seeds.prefecture:PREFECTURE_CHOICES"))
    venue = fields.TextField(label=u"開催場所(詳細)")
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
        get_label=lambda obj: obj.label or u"--なし--")

    hierarchy = fields.SelectField(label=u"階層", choices=[(x, x) for x in [u"大", u"中", u"小"]])
    label = fields.TextField(label=u"label")
    imgsrc = fields.TextField(label=u"imgsrc(e.g. /static/ticketstar/img/common/header_nav_top.gif)")
    url = fields.TextField(label=u"リンク(外部ページのURL)")
    pageset = dynamic_query_select_field_factory(
        PageSet, allow_blank=False, label=u"リンク先ページ(CMSで作成したもの)",
        get_label=lambda obj: obj.name or u"--なし--")

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


def existing_pages():
    ##本当は、client.id, site.idでfilteringする必要がある
    ##本当は、日付などでfilteringする必要がある
    ## lib.formhelpersの中で絞り込みを追加してる。
    return Page.query.filter(Page.event_id==None)


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
    publish_open_on = fields.DateTimeField(label=u"公開開始日", validators=[required_field()])
    publish_close_on = fields.DateTimeField(label=u"公開終了日", validators=[required_field()])
    text = fields.TextField(label=u"内容", validators=[required_field()], widget=widgets.TextArea())
    
    orderno = fields.IntegerField(label=u"表示順序(1〜100)", default=50)
    is_vetoed = fields.BooleanField(label=u"公開禁止")

    page = dynamic_query_select_field_factory(Page, 
                                              label=u"イベント以外のページ",
                                              query_factory=existing_pages, 
                                              allow_blank=True, 
                                              get_label=lambda obj: obj.title or u"名前なし")
    event = dynamic_query_select_field_factory(Event, 
                                               label=u"イベント",
                                               allow_blank=True, 
                                               get_label=lambda obj: obj.title or u"名前なし")


class TopcontentForm(Form):
    title = fields.TextField(label=u"タイトル", validators=[required_field()])
    publish_open_on = fields.DateTimeField(label=u"公開開始日", validators=[required_field()])
    publish_close_on = fields.DateTimeField(label=u"公開終了日", validators=[required_field()])
    text = fields.TextField(label=u"内容", validators=[required_field()], widget=widgets.TextArea())
    
    orderno = fields.IntegerField(label=u"表示順序(1〜100)", default=50)
    is_vetoed = fields.BooleanField(label=u"公開禁止")

    ##本当は、client.id, site.idでfilteringする必要がある
    page = dynamic_query_select_field_factory(Page, label=u"ページ", allow_blank=True, 
                                              get_label=lambda obj: obj.title or u"名前なし")
    image_asset = dynamic_query_select_field_factory(ImageAsset,label=u"画像", allow_blank=True)
    kind = fields.SelectField(label=u"種別", choices=[(x, x) for x in Topcontent.KIND_CANDIDATES])
    subkind = fields.TextField(label=u"サブ分類")
    countdown_type = fields.SelectField(label=u"カウントダウンの種別", choices=Topcontent.COUNTDOWN_CANDIDATES)    
    
