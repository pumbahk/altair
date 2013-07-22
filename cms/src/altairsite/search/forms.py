#-*- coding:utf-8 -*-
from datetime import datetime
from datetime import timedelta
from collections import namedtuple
from altaircms.formhelpers import Form
from wtforms import fields
from wtforms import widgets
from wtforms import validators

from altaircms.formhelpers import CheckboxListField as NewCheckboxListField
from .formparts import PutOnlyWidget
from .formparts import CheckboxWithLabelInput
from altaircms.formhelpers import MaybeSelectField
from ..pyramidlayout import get_salessegment_kinds
from ..pyramidlayout import get_top_category_genres

import logging
logger = logging.getLogger()
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


years = [(i, unicode(i)) for i in range(2013, 2020)]
months = [(i, unicode(i)) for i in range(1, 13)]
days = [(i, unicode(i)) for i in range(1, 32)]

PREF_DICT = {
    "hokkaido": import_symbol("altaircms.seeds.area.hokkaido:HOKKAIDO_CHOICES"),
    "tohoku": import_symbol("altaircms.seeds.area.tohoku:TOHOKU_CHOICES"),
    "kitakanto": import_symbol("altaircms.seeds.area.kitakanto:KITAKANTO_CHOICES"),
    "shutoken": import_symbol("altaircms.seeds.area.shutoken:SHUTOKEN_CHOICES"),
    "koshinetsu": import_symbol("altaircms.seeds.area.koshinetsu:KOSHINETSU_CHOICES"),
    "hokuriku": import_symbol("altaircms.seeds.area.hokuriku:HOKURIKU_CHOICES"),
    "tokai": import_symbol("altaircms.seeds.area.tokai:TOKAI_CHOICES"),
    "kinki": import_symbol("altaircms.seeds.area.kinki:KINKI_CHOICES"),
    "chugoku": import_symbol("altaircms.seeds.area.chugoku:CHUGOKU_CHOICES"),
    "shikoku": import_symbol("altaircms.seeds.area.shikoku:SHIKOKU_CHOICES"),
    "kyushu": import_symbol("altaircms.seeds.area.kyushu:KYUSHU_CHOICES"),
    "okinawa": import_symbol("altaircms.seeds.area.okinawa:OKINAWA_CHOICES"),
}


## 日本語へ変化する辞書
PREF_EN_TO_JA = {}
PREF_EN_TO_JA.update(import_symbol("altaircms.seeds.area:AREA_CHOICES"))
PREF_EN_TO_JA.update(import_symbol("altaircms.seeds.prefecture:PREFECTURE_CHOICES"))
##


def parse_date(y, m, d):
    if d <= 0:
        d = 1
    try:
        return datetime(int(y), int(m), int(d))
    except UnicodeEncodeError:
        return None
    except ValueError:
        try:
            m = int(m)
            if m == 12:
                return datetime(int(y)+1, 1, 1) - timedelta(days=1)
            else:
                return datetime(int(y), m+1, 1) - timedelta(days=1)
        except ValueError:
            return None

def create_close_date(close_date):
    if close_date:
        close_date = close_date + timedelta(days=1)
        close_date = close_date - timedelta(minutes=1)
    return close_date

### toppage sidebar
class TopPageSidebarSearchForm(Form):
    """ top page のsidebarのform"""
    start_year = MaybeSelectField(blank_text=u'年', blank_value="",choices=years)
    start_month = MaybeSelectField(blank_text=u'月', choices=months)
    start_day = MaybeSelectField(blank_text=u'日', choices=days)

    end_year = MaybeSelectField(blank_text=u'年', blank_value="",choices=years)
    end_month = MaybeSelectField(blank_text=u'月', choices=months)
    end_day = MaybeSelectField(blank_text=u'日', choices=days)
    choices = import_symbol("altaircms.seeds.area:AREA_CHOICES")
    area = fields.SelectField(choices=[("", "-------")]+choices)

    def make_query_params(self):
        data = self.data
        performance_open, performance_close = None, None
        if all((data["start_year"], data["start_month"], data["start_day"])):
            performance_open = parse_date(data["start_year"], data["start_month"], data["start_day"])
        if all((data["end_year"], data["end_month"], data["end_day"])):
            performance_close = parse_date(data["end_year"], data["end_month"], data["end_day"])
        if performance_open and performance_close and performance_open > performance_close:
            performance_open, performance_close = performance_close, performance_open
        performance_close = create_close_date(performance_close)

        params =  {
            "performance_open": performance_open, 
            "performance_close": performance_close, 
            }
        
        if data["area"] and data["area"] != u"None":
            areas = params["areas"] = [data["area"]]
            prefs = params["prefectures"] = [x for x,_ in  PREF_DICT.get(data["area"], [])]
            params["area_tree"] = MarkedTree(check_all_list=areas, 
                                             translator=PREF_EN_TO_JA, 
                                             tree=zip(areas, prefs))
        return params



## todo:フリーワード
## todo: make query
class QueryPartForm(Form):
    query = fields.TextField(id="freeword_query", label=u"",)
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
class GenrePartForm(Form):
    top = NewCheckboxListField(choices=[])
    sub = NewCheckboxListField(choices=[])

    def configure(self, request):
        genres = get_top_category_genres(request)
        self.top.choices = [(unicode(g.id), g.label) for g in genres]
        self.for_render_subs = [[(unicode(x.id), x.label) for x in g.children] for g in genres]
        self.sub.choices = [x for xs in self.for_render_subs for x in xs]
        return self

    def ids_from_choices(self, choices):
        return [p[0] for p in choices]

    def make_query_params(self):
        self.validate()
        subs = self.data["sub"]
        sub_genre_id_list = [[x for x in subs if x in self.ids_from_choices(cands)] for cands in self.for_render_subs]

        label_dict = dict(self.top.choices)
        label_dict.update(self.sub.choices)

        return {"top_categories": self.data["top"], 
                "sub_categories": self.data["sub"], 
                "category_tree": MarkedTree(check_all_list=self.data["top"],
                                            translator=label_dict, 
                                            tree=zip(self.ids_from_choices(self.top.choices), sub_genre_id_list)) ## for rendering html
                }

    def __html__(self): ## todo refactoring
        """top と sub NewCheckboxListFieldと合わせて"""
        html = []
        prefix = self._prefix or ""
        for (t_id, t_label), subs in zip(self.top.choices, self.for_render_subs):
            html.append(u"<tr>")
            html.append(u'<td class="mostleft"><span class="control-group"><label><input name="%stop" value="%s" type="checkbox"/> %s</label></span></td>' % (prefix, t_id, t_label))
            html.append(u"<td>")
            for s_id, s_label in subs:
                html.append(u'<span class="control-group"><label><input name="%ssub" value="%s" type="checkbox"/> %s</label></span>' % (prefix, s_id, s_label))
            html.append(u"</td>")
            html.append(u"</tr>")
        return u"\n".join(html)
            

class AreaPartForm(Form):
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

    pref_hokkaido = NewCheckboxListField(choices=PREF_DICT["hokkaido"])
    pref_tohoku = NewCheckboxListField(choices=PREF_DICT["tohoku"])
    pref_kitakanto = NewCheckboxListField(choices=PREF_DICT["kitakanto"])
    pref_shutoken = NewCheckboxListField(choices=PREF_DICT["shutoken"])
    pref_koshinetsu = NewCheckboxListField(choices=PREF_DICT["koshinetsu"])
    pref_hokuriku = NewCheckboxListField(choices=PREF_DICT["hokuriku"])
    pref_tokai = NewCheckboxListField(choices=PREF_DICT["tokai"])
    pref_kinki = NewCheckboxListField(choices=PREF_DICT["kinki"])
    pref_chugoku = NewCheckboxListField(choices=PREF_DICT["chugoku"])
    pref_shikoku = NewCheckboxListField(choices=PREF_DICT["shikoku"])
    pref_kyushu = NewCheckboxListField(choices=PREF_DICT["kyushu"])
    pref_okinawa = NewCheckboxListField(choices=PREF_DICT["okinawa"])

    areas = ["hokkaido", "tohoku", "kitakanto", "shutoken", "koshinetsu", "hokuriku", "tokai", "kinki", "chugoku", "shikoku", "kyushu", "okinawa"]


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
                                        translator=PREF_EN_TO_JA)
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

class PerformanceTermPartForm(Form):
    start_year = MaybeSelectField(blank_value="",choices=years)
    start_month = MaybeSelectField(choices=months)
    start_day = MaybeSelectField(choices=days)

    end_year = MaybeSelectField(blank_value="",choices=years)
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
            performance_open = parse_date(data["start_year"], data["start_month"], data["start_day"])
        if all((data["end_year"], data["end_month"], data["end_day"])):
            performance_close = parse_date(data["end_year"], data["end_month"], data["end_day"])
        if performance_open and performance_close and performance_open > performance_close:
            performance_open, performance_close = performance_close, performance_open

        performance_close = create_close_date(performance_close)
        return {"performance_open": performance_open,
                "performance_close": performance_close}

## todo:販売条件
class DealCondPartForm(Form):
    deal_cond = NewCheckboxListField(choices=[])
    def configure(self, request):
        self.deal_cond.choices = [(unicode(k.id), k.label) for k in get_salessegment_kinds(request)]
        return self

    def __html__(self):
        return u"%(deal_cond)s" % self

    def make_query_params(self):
        self.validate()
        return self.data

## todo:付加サービス
class AddedServicePartForm(Form):
    choices = [("select-seat", u"座席選択可能"), ("keep-adjust", u"お隣キープ"), ("2d-market", u"2次市場")]
    choices = []
    added_services = NewCheckboxListField(choices=choices)

    def __html__(self):
        return u"%(added_services)s" % self

    def make_query_params(self):
        import warnings
        warnings.warn("these flag are not support yet.")
        return {"added_service": []}


## todo:発売日,  rename
class AboutDealPartForm(Form):
    before_deal_start = MaybeSelectField(choices=days)
    till_deal_end = MaybeSelectField(choices=days)
    
    closed_only = fields.BooleanField(label=u"販売終了した公演", widget=CheckboxWithLabelInput())
    canceled_only = fields.BooleanField(label=u"中止した公演", widget=CheckboxWithLabelInput())

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
    def __init__(self, request, formdata=None):
        self.request = request
        self._forms = []
        self.query = self._append_with(QueryPartForm(formdata=formdata, prefix="q-"))
        self.genre = self._append_with(GenrePartForm(formdata=formdata, prefix="g-"))
        self.area = self._append_with(AreaPartForm(formdata=formdata, prefix="a"))
        self.performance_term = self._append_with(PerformanceTermPartForm(formdata=formdata, prefix="pt-"))
        self.deal_cond = self._append_with(DealCondPartForm(formdata=formdata, prefix="dc-"))
        self.added_service = self._append_with(AddedServicePartForm(formdata=formdata, prefix="as-"))
        self.about_deal = self._append_with(AboutDealPartForm(formdata=formdata, prefix="ad-"))

    def _append_with(self, form):
        self._forms.append(form)
        if hasattr(form, "configure"):
            form.configure(self.request)
        return form

    def validate(self):
        return all(form.validate() for form in self._forms)

    def make_query_params(self):
        params = {}
        for form in self._forms:
            params.update(form.make_query_params())
        return params

def get_search_forms(request, formdata=None):
    return DetailSearchQueryForm(request, formdata)
    
def form_as_filter(qs, form):
    return form.as_filter(qs)

