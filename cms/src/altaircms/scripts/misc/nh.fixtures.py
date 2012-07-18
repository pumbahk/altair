# -*- coding:utf-8 -*-

"""
nh用のデータ作成。巨大になったら死亡
"""
import itertools
import sys
import functools
import sqlalchemy as sa
from pyramid.decorator import reify
from datetime import datetime

import tableau as t
from tableau.sqla import newSADatum
from tableau import DataWalker
from tableau.sql import SQLGenerator
from altaircms.scripts.misc.dataset import DataSuite, WithCallbackDataSet

import sqlahelper
import altaircms.models

import altaircms.event.models
import altaircms.page.models
import altaircms.layout.models

# sqlahelper.add_engine(sa.create_engine("sqlite://"))
# sqlahelper.get_base().metadata.create_all()
sqlahelper.add_engine(sa.create_engine("mysql+pymysql://altaircms:altaircms@localhost/altaircms?charset=utf8"))


def build_dict(items, k):
    return {getattr(e, k):e for e in items}

class FixtureBuilder(object):
    def __init__(self, Datum):
        class _Datum(Datum):
            def __init__(self, schema, **fields):
                Datum.__init__(self, schema, t.auto("id"), **fields)
        self.Datum = _Datum
        self._Datum = Datum

        class Default(object):
            created_at=datetime(1900, 1, 1)
            updated_at=datetime(1900, 1, 1) 
            publish_begin=datetime(1900, 1, 1)
        self.Default = Default

class Result(object):
    def __init__(self, result, cache):
        self.result = result
        self.cache = cache

    def __iter__(self):
        return iter(self.result)

class BjNHFixtureBuilder(FixtureBuilder):
    def __init__(self, Datum):
        """
        layout_triples: (title, template_filename, blocks)
        page_triples: (name, url, layout)
        category_items: (orderno, name, label, hierarchy, page_name)
        """
        super(BjNHFixtureBuilder, self).__init__(Datum)
        layout_triples = [
            (u'nhシンプル', 'nh.base.mako', '[["header"], ["kadomaru"]]'), 
            (u'nh.introduction','nh.introduction.mako', '[["header"], ["kadomaru"], ["card_and_QR"],["card_and_seven"],["card_and_home"],["card_and_onsite"]]'),
            ]
        self.layout_triples = layout_triples

        page_triples = [
            (u"nh:準備中", "before", u"nhシンプル"),
            (u"nh:よくある質問", "faq", u"nhシンプル"),
            (u"nh:チケット新登場(introduction)", "introduction", u"nh.introduction"),
            (u"nh:受付履歴確認", "order/history", u"nhシンプル"),
            (u"nh:予約購入完了(カード)", "register/purcharsed/credit", u"nhシンプル"),
            (u"nh:予約購入完了(セブン)", "register/purcharsed/seven", u"nhシンプル"),
            (u"nh:チケットトップ", "tickets/top", u"nhシンプル"),
            (u"nh:チケット購入・引き取り方法", "purcharsed/credit", u"nhシンプル"),
            (u"nh:ブースタークラブ申込", "purcharsed/seven", u"nhシンプル"),
            ]
        self.page_triples = page_triples

        category_items = [
            (1, "top", u"チケットTOP", "header_menu", u"nh:チケットトップ", ), 
            (2, "order_way",  u"チケット購入・引き取り方法", "header_menu", u"nh:チケット購入・引き取り方法"), ##?
            (3, "register_club",  u"ブースタークラブ申込", "header_menu", u"nh:ブースタークラブ申込"), ##?
            (4, "faq",  u"よくある質問", "header_menu", u"nh:よくある質問"), 
            ]
        self.category_items = category_items
        self.organization_id = 2 ## fixme

    @reify
    def build_layout(self):
        retval =  [self.Datum("layout", 
                           title=title, 
                           template_filename=template_filename, 
                           blocks=blocks, 
                           organization_id=self.organization_id, 
                           created_at=self.Default.created_at, 
                           updated_at=self.Default.updated_at)\
                       for title, template_filename, blocks in self.layout_triples]
        result = Result(retval, build_dict(retval, "title"))
        return result

    @reify
    def build_pageset(self):
        retval = [self.Datum("pagesets", 
                             name=name, 
                             organization_id=self.organization_id, 
                             version_counter=0, 
                             url=url)\
                      for name, url, layout_name in self.page_triples]
        result = Result(retval, build_dict(retval, "name"))
        return result

    @reify
    def build_page(self):       
        layouts = self.build_layout.cache
        pagesets = self.build_pageset.cache
        retval = [self.Datum("page", 
                  name=name, 
                  title=name, 
                  url=url, 
                  description="", 
                  pageset=t.many_to_one(pagesets[name], "pageset_id"), 
                  keywords="", 
                  structure="[]", 
                  version=0, 
                  published=True, 
                  publish_begin=self.Default.publish_begin, 
                  created_at=self.Default.created_at, 
                  updated_at=self.Default.updated_at, 
                  organization_id=self.organization_id, 
                  layout_id=layouts[layout_name])
                      for name, url, layout_name in self.page_triples]
        result = Result(retval, build_dict(retval, "name"))
        return result
        
    @reify
    def build_category(self):
        pagesets = self.build_pageset.cache
        retval = [self.Datum("category", 
                             orderno=orderno, 
                             organization_id=self.organization_id, 
                             name=name, 
                             label=label, 
                             hierarchy=hierarchy, 
                             pageset_id=pagesets.get(page_name)
                             )
                  for orderno, name, label, hierarchy, page_name in self.category_items]
        result = Result(retval, build_dict(retval, "name"))
        return result

    
    def build(self):
        return itertools.chain.from_iterable([
                self.build_layout, 
                self.build_pageset, 
                self.build_page, 
                self.build_category
                ], )
                 
class WithOffset(object):
    """ insert sql id with offset value

    e.g. offset = 10
    insert statment start from id=11
    """
    def __init__(self):
        self.offset_table = {}
        self.session = sqlahelper.get_session()
        self.table_to_declarative = self.collect_declarative(sqlahelper.get_base())

    def collect_declarative(self, base):
        table_to_declarative = {}
        if base is not None:
            for class_name, declarative in base._decl_class_registry.items():
                table_to_declarative[declarative.__table__.name] = declarative
        return table_to_declarative

    def _get_offset_value(self, schema, data):
        cls = self.table_to_declarative[schema]
        return cls.query.with_entities(sa.func.Max(cls.id)).scalar() or 0

    def get_offset_value(self, schema, data): #memoize function
        if not schema in self.offset_table:
            self.offset_table[schema] = self._get_offset_value(schema, data)
        return self.offset_table[schema]
        
    def setvalue(self, dataset, data):
        schema = data._tableau_table.name
        offset = self.get_offset_value(schema, data)
        pk = dataset.seq + offset
        setattr(datum, datum._tableau_id_fields[0], pk)
        assert getattr(datum, datum._tableau_id_fields[0], pk)


Base = sqlahelper.get_base()
Session = sqlahelper.get_session()
Datum = newSADatum(Base.metadata, Base)

builder = BjNHFixtureBuilder(Datum)
suite = DataSuite(dataset_impl=functools.partial(WithCallbackDataSet, on_autoid=WithOffset()))
walker = DataWalker(suite)

for datum in builder.build():
    walker(datum)
SQLGenerator(sys.stdout, encoding='utf-8')(suite)
