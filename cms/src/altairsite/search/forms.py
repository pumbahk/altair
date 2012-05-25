#-*- coding:utf-8 -*-
from datetime import datetime
from collections import namedtuple
from wtforms import form
from wtforms import fields
from wtforms import widgets
from wtforms import validators

from .formparts import CheckboxListField
from .formparts import PutOnlyWidget
from .formparts import CheckboxWithLabelInput
from .formparts import MaybeSelectField

import pkg_resources
def import_symbol(symbol):
    return pkg_resources.EntryPoint.parse("x=%s" % symbol).load(False)

"""
MarkedTree:検索式の表示に使う
area_tree = MarkedTree(check_all_list=["関東"], tree=[("関東": [...]), ("北海道", ["hokkaaido"])])

検索条件をhtmlとしてレンダリングするときに(resource.QueryParamsRender)使う
   「関東 > 全て, 北海道 > 北海道」
というように表示される
convertorはローマ字->日本語の変換などに使われる
"""
MarkedTree = namedtuple("MarkedTree", "check_all_list, tree, translator")


## todo:フリーワード
## todo: make query
class QueryPartForm(form.Form):
    query = fields.TextField(label=u"",)
    query_cond = fields.RadioField(choices=[("intersection", u"全てを含む"), ("union", u"少なくとも1つを含む")], 
                                   widget=PutOnlyWidget())

    def __html__(self):
        return u"%(query)s %(query_cond)s" % self

    def make_query_params(self):
        params = self.data
        query = params.get("query")
        query_cond = params.get("query_cond")

        if not query:
            return {}
        if query_cond not in ("intersection", "union"):
            params["query_cond"] = "intersection"
        return params

## todo:ジャンル
## todo: make query
class GenrePartForm(form.Form):
    music = fields.BooleanField(label=u"音楽", widget=CheckboxWithLabelInput())
    music_subgenre_choices = import_symbol("altaircms.seeds.categories.music:MUSIC_SUBCATEGORY_CHOICES")
    music_subgenre = CheckboxListField(choices=music_subgenre_choices)

    stage = fields.BooleanField(label=u"演劇", widget=CheckboxWithLabelInput())
    stage_subgenre_choices = import_symbol("altaircms.seeds.categories.stage:STAGE_SUBCATEGORY_CHOICES")
    stage_subgenre = CheckboxListField(choices=stage_subgenre_choices)

    sports = fields.BooleanField(label=u"スポーツ", widget=CheckboxWithLabelInput())
    sports_subgenre_choices = import_symbol("altaircms.seeds.categories.sports:SPORTS_SUBCATEGORY_CHOICES")
    sports_subgenre = CheckboxListField(choices=sports_subgenre_choices)

    other = fields.BooleanField(label=u"イベント・その他", widget=CheckboxWithLabelInput())
    other_subgenre_choices = import_symbol("altaircms.seeds.categories.other:OTHER_SUBCATEGORY_CHOICES")
    other_subgenre = CheckboxListField(choices=other_subgenre_choices)

    ## 日本語へ変換する辞書
    en_to_ja = {}
    en_to_ja.update(music_subgenre_choices)
    en_to_ja.update(sports_subgenre_choices)
    en_to_ja.update(stage_subgenre_choices)
    en_to_ja.update(other_subgenre_choices)
    en_to_ja.update(music=u"音楽", stage=u"演劇", sports=u"スポーツ", other=u"イベント・その他")
    ##

    def make_query_params(self):
        data = self.data
        genres = ["music", "stage", "sports", "other"]
        sub_genres = [data["music_subgenre"], data["stage_subgenre"], data["sports_subgenre"], data["other_subgenre"]]
        top_categories = [k for k in genres if data[k]]
        return {"top_categories": top_categories, 
                "sub_categories": list(set([x for xs in sub_genres if xs for x in xs])), 
                "category_tree": MarkedTree(check_all_list=top_categories,
                                            translator=self.en_to_ja, 
                                            tree=zip(genres, sub_genres)) ## for rendering html
                }

    def __html__(self): ## todo refactoring
        return u"""
<tr>
  <td class="mostleft">%(music)s</td>
  <td>%(music_subgenre)s</td>
</tr>
<tr>
  <td class="mostleft">%(stage)s</td>
  <td>%(stage_subgenre)s</td>
</tr>
<tr>
  <td class="mostleft">%(sports)s</td>
  <td>%(sports_subgenre)s</td>
</tr>
<tr>
  <td class="mostleft">%(other)s</td>
  <td>%(other_subgenre)s</td>
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

    ## 日本語へ変化する辞書
    en_to_ja = {}
    en_to_ja.update(import_symbol("altaircms.seeds.area:AREA_CHOICES"))
    en_to_ja.update(import_symbol("altaircms.seeds.prefecture:PREFECTURE_CHOICES"))
    ##

    def make_query_params(self):
        data = self.data
        prefectures = set()
        areas = []
        area_tree = []
        for k in self.areas:
            if data[k]:
                areas.append(k)
                ## areaがチェックされていたら、その区分にある県を全て格納する
                prefectures.update([p for p, _ in getattr(self, "pref_"+k).choices])

            ## checkされた県の内容がdataの中に入っている(CheckboxListField)
            vs = data["pref_"+k]
            area_tree.append((k, vs))
            if vs:
                prefectures.update(vs)

        return {"areas": areas, 
                "prefectures": list(prefectures), 
                "area_tree": MarkedTree(check_all_list=areas, tree=area_tree, 
                                        translator=self.en_to_ja)
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
    start_year = MaybeSelectField(choices=years)
    start_month = MaybeSelectField(choices=months)
    start_day = MaybeSelectField(choices=days)

    end_year = MaybeSelectField(choices=years)
    end_month = MaybeSelectField(choices=months)
    end_day = MaybeSelectField(choices=days)

    def __html__(self):
        return u"""
%(start_year)s年%(start_month)s月%(start_day)s日 〜 %(end_year)s年%(end_month)s月%(end_day)s日
""" % self

    def make_query_params(self):
        data = self.data
        performance_open, performance_close = None, None
        if all((data["start_year"], data["start_month"], data["start_day"])):
            performance_open = datetime(*(int(x) for x in (data["start_year"], data["start_month"], data["start_day"])))
        if all((data["end_year"], data["end_month"], data["end_day"])):
            performance_close = datetime(*(int(x) for x in (data["end_year"], data["end_month"], data["end_day"])))
        return {"performance_open": performance_open, 
                "performance_close": performance_close}

## todo:販売条件
class DealCondPartForm(form.Form):
    #deal_cond_choices=[("early", u"先行"), ("normal", u"一般")]
    deal_cond_choices=[("first_lottery", u"最速抽選"),
                       ("early_lottery", u"先行抽選"), 
                       ("eary_fisrtcome", u"先行先着"), 
                       ("normal", u"一般販売"), 
                       ("added_lottery", u"追加抽選")]
    DDICT = dict(deal_cond_choices)

    deal_cond = fields.RadioField(choices=deal_cond_choices, 
                                   widget=PutOnlyWidget())

    def __html__(self):
        return u"%(deal_cond)s" % self

    def make_query_params(self):
        import warnings
        warnings.warn("these flag are not support yet.")
        return self.data

## todo:付加サービス
class AddedServicePartForm(form.Form):
    choices = [("select-seat", u"座席選択可能"), ("keep-adjust", u"お隣キープ"), ("2d-market", u"2次市場")]
    added_services = CheckboxListField(choices=choices)

    def __html__(self):
        return u"%(added_services)s" % self

    def make_query_params(self):
        import warnings
        warnings.warn("these flag are not support yet.")
        return {"added_service": []}


## todo:発売日,  rename
class AboutDealPartForm(form.Form):
    before_deal_start = MaybeSelectField(choices=days)
    till_deal_end = MaybeSelectField(choices=days)
    
    closed_only = fields.BooleanField(label=u"販売終了", widget=CheckboxWithLabelInput())
    canceled_only = fields.BooleanField(label=u"公演中止", widget=CheckboxWithLabelInput())

    def __html__(self):
        return u"""
<ul>
  <li>
    %(before_deal_start)s日以内に受付・販売開始
  </li>
  <li>
    販売終了まで%(till_deal_end)s日
  </li>
  <li>
    %(closed_only)s %(canceled_only)s
  </li>
</ul>
""" % self

    def make_query_params(self):
        return self.data

class DetailSearchQueryForm(object):
    def __init__(self, formdata=None):
        self._forms = []
        self.query = self._append_with(QueryPartForm(formdata=formdata))
        self.genre = self._append_with(GenrePartForm(formdata=formdata))
        self.area = self._append_with(AreaPartForm(formdata=formdata))
        self.performance_term = self._append_with(PerformanceTermPartForm(formdata=formdata))
        self.deal_cond = self._append_with(DealCondPartForm(formdata=formdata))
        self.added_service = self._append_with(AddedServicePartForm(formdata=formdata))
        self.about_deal = self._append_with(AboutDealPartForm(formdata=formdata))

    def _append_with(self, form):
        self._forms.append(form)
        return form

    def validate(self):
        return all(form.validate() for form in self._forms)

    def make_query_params(self):
        params = {}
        for form in self._forms:
            params.update(form.make_query_params())
        return params

def get_search_forms(formdata=None):
    return DetailSearchQueryForm(formdata)
    
def form_as_filter(qs, form):
    return form.as_filter(qs)

