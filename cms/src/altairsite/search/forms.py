#-*- coding:utf-8 -*-
from wtforms import form
from wtforms import fields
from wtforms import widgets
from wtforms import validators

from .formparts import CheckboxListField

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
    music = fields.BooleanField(label=u"音楽")
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

            
## todo:開催地
class AreaPartForm(form.Form):
    area = CheckboxListField
    
    area_hokaido = fields.BooleanField(label=u"北海道")
    area_tohoku = fields.BooleanField(label=u"東北")
    area_kanto = fields.BooleanField(label=u"関東・甲信越")
    area_chubu = fields.BooleanField(label=u"中部・東海")
    area_kinki = fields.BooleanField(label=u"近畿・北陸")
    area_chugoku = fields.BooleanField(label=u"中国・四国")
    area_kyushu = fields.BooleanField(label=u"九州沖縄")

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

## todo:公演日
## todo:販売条件
## todo:付加サービス
## todo:発売日

