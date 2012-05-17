#-*- coding:utf-8 -*-
from wtforms import form
from wtforms import fields
from wtforms import widgets
from wtforms import validators

from .formparts import CheckboxListField
from .formparts import CheckboxWithLabelInput

import pkg_resources
def import_symbol(symbol):
    return pkg_resources.EntryPoint.parse("x=%s" % symbol).load(False)

## todo:フリーワード
class QueryPartForm(form.Form):
    query = fields.TextField(label=u"")
    query_cond = fields.RadioField(choices=[("intersection", u"全てを含む"), ("union", u"少なくとも1つを含む")])

    def __html__(self):
        return u"%(query)s %(query_cond)s"

## todo:ジャンル
class GanrePartForm(form.Form):
    music = fields.BooleanField(label=u"音楽", widget=CheckboxWithLabelInput())
    music_subganre_choices = import_symbol("altaircms.seeds.categories.music:MUSIC_SUBCATEGORY_CHOICES")
    music_subganre = CheckboxListField(choices=music_subganre_choices)

    stage = fields.BooleanField(label=u"演劇")
    stage_subganre_choices = import_symbol("altaircms.seeds.categories.stage:STAGE_SUBCATEGORY_CHOICES")
    stage_subganre = CheckboxListField(choices=stage_subganre_choices)

    sports = fields.BooleanField(label=u"スポーツ")
    sports_subganre_choices = import_symbol("altaircms.seeds.categories.sports:SPORTS_SUBCATEGORY_CHOICES")
    sports_subganre = CheckboxListField(choices=sports_subganre_choices)

    other = fields.BooleanField(label=u"イベント・その他")
    other_subganre_choices = import_symbol("altaircms.seeds.categories.other:OTHER_SUBCATEGORY_CHOICES")
    other_subganre = CheckboxListField(choices=other_subganre_choices)

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
class AreaPartForm(form.Form):
    def __html__(self):
        return u"this-is-dummy"

# class AreaPartForm(form.Form):
#     area_hokkaido = fields.BooleanField(label=u"北海道")
#     area_tohoku = fields.BooleanField(label=u"東北")
#     area_kanto = fields.BooleanField(label=u"関東・甲信越")
#     area_chubu = fields.BooleanField(label=u"中部・東海・北陸")
#     area_kinki = fields.BooleanField(label=u"近畿")
#     area_chugoku = fields.BooleanField(label=u"中国・四国")
#     area_kyushu = fields.BooleanField(label=u"九州沖縄")

#     pref_hokkaido = CheckboxListField(choices=import_symbol("altaircms.seeds.area.hokkaido:HOKKAIDO_CHOICES"))
#     pref_tohoku = CheckboxListField(choices=import_symbol("altaircms.seeds.area.tohoku:TOHOKU_CHOICES"))
#     pref_kanto = CheckboxListField(choices=import_symbol("altaircms.seeds.area.kanto:KANTO_CHOICES"))
#     pref_chubu = CheckboxListField(choices=import_symbol("altaircms.seeds.area.chubu:CHUBU_CHOICES"))
#     pref_kinki = CheckboxListField(choices=import_symbol("altaircms.seeds.area.kinki:KINKI_CHOICES"))
#     pref_chugoku = CheckboxListField(choices=import_symbol("altaircms.seeds.area.chugoku:CHUGOKU_CHOICES"))
#     pref_kyushu = CheckboxListField(choices=import_symbol("altaircms.seeds.area.kyushu:KYUSHU_CHOICES"))

#     def __html__(self): ## todo refactoring
#         return u"""
# <tr>
#   <td class="mostleft">%(area_hokkaido)s</td>
#   <td>%(preef_hokkaido)s</td>
# </tr>
# <tr>
#   <td class="mostleft">%(area_tohoku)s</td>
#   <td>%(preef_tohoku)s</td>
# </tr>
# <tr>
#   <td class="mostleft">%(area_kanto)s</td>
#   <td>%(preef_kanto)s</td>
# </tr>
# <tr>
#   <td class="mostleft">%(area_chubu)s</td>
#   <td>%(preef_chubu)s</td>
# </tr>
# <tr>
#   <td class="mostleft">%(area_kinki)s</td>
#   <td>%(preef_kinki)s</td>
# </tr>
# <tr>
#   <td class="mostleft">%(area_chugokou)s</td>
#   <td>%(preef_chugokou)s</td>
# </tr>
# <tr>
#   <td class="mostleft">%(area_kyushu)s</td>
#   <td>%(preef_kyushu)s</td>
# </tr>
# """ % self

## todo:公演日
class PerformanceTermPartForm(form.Form):
    years = [(i, unicode(i)) for i in range(2010, 2020)]
    months = [(i, unicode(i)) for i in range(1, 13)]
    days = [(i, unicode(i)) for i in range(1, 32)]
                  
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
class SalesCondPartForm(form.Form):
    pass

## todo:付加サービス
class AddedServicePartForm(form.Form):
    pass

## todo:発売日,  rename
class AboutSalesDatePartForm(form.Form):
    pass

def get_search_forms():
    class forms(object):
        query = QueryPartForm()
        ganre = GanrePartForm()
        area = AreaPartForm()
        performance_term = PerformanceTermPartForm()
        sales_cond = SalesCondPartForm()
        added_service = AddedServicePartForm()
        about_sales_date = AboutSalesDatePartForm()
    return forms
