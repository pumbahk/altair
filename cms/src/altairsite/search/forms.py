#-*- coding:utf-8 -*-
from wtforms import form
from wtforms import fields
from wtforms import widgets
from wtforms import validators

from .formparts import CheckboxListField
from .formparts import PutOnlyWidget
from .formparts import CheckboxWithLabelInput

import pkg_resources
def import_symbol(symbol):
    return pkg_resources.EntryPoint.parse("x=%s" % symbol).load(False)

## todo:フリーワード
## todo: make query
class QueryPartForm(form.Form):
    query = fields.TextField(label=u"",)
    query_cond = fields.RadioField(choices=[("intersection", u"全てを含む"), ("union", u"少なくとも1つを含む")], 
                                   widget=PutOnlyWidget())

    def __html__(self):
        return u"%(query)s %(query_cond)s" % self

## todo:ジャンル
#3 todo: make query
class GanrePartForm(form.Form):
    music = fields.BooleanField(label=u"音楽", widget=CheckboxWithLabelInput())
    music_subganre_choices = import_symbol("altaircms.seeds.categories.music:MUSIC_SUBCATEGORY_CHOICES")
    music_subganre = CheckboxListField(choices=music_subganre_choices)

    stage = fields.BooleanField(label=u"演劇", widget=CheckboxWithLabelInput())
    stage_subganre_choices = import_symbol("altaircms.seeds.categories.stage:STAGE_SUBCATEGORY_CHOICES")
    stage_subganre = CheckboxListField(choices=stage_subganre_choices)

    sports = fields.BooleanField(label=u"スポーツ", widget=CheckboxWithLabelInput())
    sports_subganre_choices = import_symbol("altaircms.seeds.categories.sports:SPORTS_SUBCATEGORY_CHOICES")
    sports_subganre = CheckboxListField(choices=sports_subganre_choices)

    other = fields.BooleanField(label=u"イベント・その他", widget=CheckboxWithLabelInput())
    other_subganre_choices = import_symbol("altaircms.seeds.categories.other:OTHER_SUBCATEGORY_CHOICES")
    other_subganre = CheckboxListField(choices=other_subganre_choices)

    def make_query(self):
        data = self.data
        sub_ganres = [data["music_subganre"], data["stage_subganre"], data["sports_subganre"], data["other_subganre"]]
        return {"top_categories": [k for k in ["music", "stage", "sports", "other"] if data[k]], 
                "sub_categories": list(set([x for xs in sub_ganres for x in xs]))
                }

    def __html__(self): ## todo refactoring
        return u"""
<tr>
  <td class="mostleft">%(music)s</td>
  <td>%(music_subganre)s</td>
</tr>
<tr>
  <td class="mostleft">%(stage)s</td>
  <td>%(stage_subganre)s</td>
</tr>
<tr>
  <td class="mostleft">%(sports)s</td>
  <td>%(sports_subganre)s</td>
</tr>
<tr>
  <td class="mostleft">%(other)s</td>
  <td>%(other_subganre)s</td>
</tr>
""" % self
            
# todo:開催地
# class AreaPartForm(form.Form):
#     def __html__(self):
#         return u"this-is-dummy"

class AreaPartForm(form.Form):
    hokkaido = fields.BooleanField(label=u"北海道", widget=CheckboxWithLabelInput()) 
    tohoku = fields.BooleanField(label=u"東北", widget=CheckboxWithLabelInput()) 
    kitakanto = fields.BooleanField(label=u"北関東", widget=CheckboxWithLabelInput()) 
    shutoken = fields.BooleanField(label=u"首都圏", widget=CheckboxWithLabelInput()) 
    koshinetsu = fields.BooleanField(label=u"甲信越", widget=CheckboxWithLabelInput()) 
    hokuriku = fields.BooleanField(label=u"北陸", widget=CheckboxWithLabelInput()) 
    tokai = fields.BooleanField(label=u"東海", widget=CheckboxWithLabelInput()) 
    kinki = fields.BooleanField(label=u"近畿", widget=CheckboxWithLabelInput()) 
    chugoku = fields.BooleanField(label=u"中国", widget=CheckboxWithLabelInput()) 
    shikoku = fields.BooleanField(label=u"四国", widget=CheckboxWithLabelInput()) 
    kyushu = fields.BooleanField(label=u"九州", widget=CheckboxWithLabelInput()) 
    okinawa = fields.BooleanField(label=u"沖縄", widget=CheckboxWithLabelInput()) 

    pref_hokkaido = CheckboxListField(choices=import_symbol("altaircms.seeds.area.hokkaido:HOKKAIDO_CHOICES"))
    pref_tohoku = CheckboxListField(choices=import_symbol("altaircms.seeds.area.tohoku:TOHOKU_CHOICES"))
    pref_kitakanto = CheckboxListField(choices=import_symbol("altaircms.seeds.area.kitakanto:KITAKANTO_CHOICES"))
    pref_shutoken = CheckboxListField(choices=import_symbol("altaircms.seeds.area.shutoken:SHUTOKEN_CHOICES"))
    pref_koshinetsu = CheckboxListField(choices=import_symbol("altaircms.seeds.area.koshinetsu:KOSHINETSU_CHOICES"))
    pref_hokuriku = CheckboxListField(choices=import_symbol("altaircms.seeds.area.hokuriku:HOKURIKU_CHOICES"))
    pref_tokai = CheckboxListField(choices=import_symbol("altaircms.seeds.area.tokai:TOKAI_CHOICES"))
    pref_kinki = CheckboxListField(choices=import_symbol("altaircms.seeds.area.kinki:KINKI_CHOICES"))
    pref_chugoku = CheckboxListField(choices=import_symbol("altaircms.seeds.area.chugoku:CHUGOKU_CHOICES"))
    pref_shikoku = CheckboxListField(choices=import_symbol("altaircms.seeds.area.shikoku:SHIKOKU_CHOICES"))
    pref_kyushu = CheckboxListField(choices=import_symbol("altaircms.seeds.area.kyushu:KYUSHU_CHOICES"))
    pref_okinawa = CheckboxListField(choices=import_symbol("altaircms.seeds.area.okinawa:OKINAWA_CHOICES"))

    areas = ["hokkaido", "tohoku", "kitakanto", "shutoken", "koshinetsu", "hokuriku", "tokai", "kinki", "chugoku", "shikoku", "kyushu", "okinawa"]    
    def make_query(self):
        data = self.data
        prefectures = set()
        areas = []

        for k in self.areas:
            if data[k]:
                areas.append(k)
                ## areaがチェックされていたら、その区分にある県を全て格納する
                prefectures.update([p for p, _ in getattr(self, "pref_"+k).choices])

            ## checkされた県の内容がdataの中に入っている(CheckboxListField)
            prefectures.update(data["pref_"+k])

        return {"areas": areas, 
                "prefectures": list(prefectures)
                }

    def __html__(self): ## todo refactoring
        fmts = (u"""\
<tr>
  <td class="mostleft">%%(%s)s</td>
  <td>%%(pref_%s)s</td>
</tr>
""" % (k, k) for k in self.areas)
        return u"".join(fmts) % self

## todo:公演日
years = [(i, unicode(i)) for i in range(2010, 2020)]
months = [(i, unicode(i)) for i in range(1, 13)]
days = [(i, unicode(i)) for i in range(1, 32)]

class PerformanceTermPartForm(form.Form):
    start_year = fields.SelectField(choices=years)
    start_month = fields.SelectField(choices=months)
    start_day = fields.SelectField(choices=days)

    end_year = fields.SelectField(choices=years)
    end_month = fields.SelectField(choices=months)
    end_day = fields.SelectField(choices=days)

    def __html__(self):
        return u"""
%(start_year)s年%(start_month)s月%(start_day)s日 〜 %(end_year)s年%(end_month)s月%(end_day)s日
""" % self

## todo:販売条件
class DealCondPartForm(form.Form):
    deal_cond = fields.RadioField(choices=[("early", u"先行"), ("normal", u"一般")], 
                                   widget=PutOnlyWidget())

    def __html__(self):
        return u"%(deal_cond)s" % self

## todo:付加サービス
class AddedServicePartForm(form.Form):
    choices = [("select-seat", u"座席選択可能"), ("keep-adjust", u"お隣キープ"), ("2d-market", u"2次市場")]
    added_services = fields.RadioField(choices=choices, widget=PutOnlyWidget())

    def __html__(self):
        return u"%(added_services)s" % self

## todo:発売日,  rename
class AboutDealPartForm(form.Form):
    before_deal_start_flg = fields.BooleanField(label=u"")
    before_deal_start = fields.SelectField(choices=days)

    till_deal_end_flg = fields.BooleanField(label=u"")
    till_deal_end = fields.SelectField(choices=days)
    
    closed_only = fields.BooleanField(label=u"販売終了", widget=CheckboxWithLabelInput())
    canceled_only = fields.BooleanField(label=u"公演中止", widget=CheckboxWithLabelInput())

    def __html__(self):
        return u"""
<ul>
  <li>
    %(before_deal_start_flg)s%(before_deal_start)s日以内に発送
  </li>
  <li>
    %(till_deal_end_flg)s販売終了まで%(till_deal_end)s日
  </li>
  <li>
    %(closed_only)s %(canceled_only)s
  </li>
</ul>
""" % self

class DetailSearchQueryForm(object):
    def __init__(self, formdata=None):
        self._forms = []
        self.query = self._append_with(QueryPartForm(formdata=formdata))
        self.ganre = self._append_with(GanrePartForm(formdata=formdata))
        self.area = self._append_with(AreaPartForm(formdata=formdata))
        self.performance_term = self._append_with(PerformanceTermPartForm(formdata=formdata))
        self.deal_cond = self._append_with(DealCondPartForm(formdata=formdata))
        self.added_service = self._append_with(AddedServicePartForm(formdata=formdata))
        self.about_deal = self._append_with(AboutDealPartForm(formdata=formdata))

    def _append_with(self, form):
        self._forms.append(form)
        return form

    def validate(self):
        return any(form.validate() for form in self._forms)

    def as_filter(self, qs=None):
        for form in self._forms:
            qs = form.as_filter(qs)
        return qs

def get_search_forms(formdata=None):
    return DetailSearchQueryForm(formdata)

def form_as_filter(qs, form):
    return form.as_filter(qs)


### search
"""
1. free wordが選択
    全文検索で検索する。copy fieldを使ってsolarで定義してた。取得されるのはpageset.id
2. ganreで選択。
2.a 大ジャンルが選択
ganre = "music"
Category.filter(Category.name==genre).filter
2.b 中ジャンルが選択
"""
from altaircms.models import Category
from altaircms.models import DBSession
from altaircms.page.models import PageSet
import sqlalchemy.orm as orm

def pagesets_by_big_category_name(name):
    parent_category_stmt = DBSession.query(Category.id).filter_by(name=name).subquery()
    parents_ids = orm.aliased(Category, parent_category_stmt)
    category_stmt = Category.query.join(parents_ids, parents_ids.id==Category.parent_id).all()


