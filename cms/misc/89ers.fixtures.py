# -*- coding:utf-8 -*-

"""
89ers用のデータ作成。巨大になったら死亡
"""
from tableau.sqla import newSADatum
import sqlahelper
import sqlalchemy as sa
# sqlahelper.add_engine(sa.create_engine("sqlite://"))
sqlahelper.add_engine(sa.create_engine("mysql+pymysql://altaircms:altaircms@localhost/altaircms?charset=utf8"))

import altaircms.models
import altaircms.event.models
import altaircms.page.models
import altaircms.layout.models
from pyramid.decorator import reify
import itertools
from datetime import datetime
import tableau as t
from tableau import DataSuite
from tableau import DataWalker
from tableau.sql import SQLGenerator, SQLBuilder
import sys

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

class Bj89ersFixtureBuilder(FixtureBuilder):
    def __init__(self, Datum):
        """
        layout_triples: (title, template_filename, blocks)
        page_doubles: (name, url)
        """
        super(Bj89ersFixtureBuilder, self).__init__(Datum)
        layout_triples = [
            ("89ers.before","89ers.before.mako", "[]"),
            ("89ers.faq","89ers.faq.mako", "[]"),
            ("89ers.introduction","89ers.introduction.mako", "[]"),
            ("89ers.order-history","89ers.order-history.mako", "[]"),
            ("89ers.purcharsed-credit","89ers.purchased-credit.mako", "[]"),
            ("89ers.purchased-seven","89ers.purchased-seven.mako", "[]"),
            ("89ers.tickets_top","89ers.tickets_top.mako", "[]"),
            ]
        self.layout_triples = layout_triples

        page_doubles = [
            ("89ers.before", "/before"),
            ("89ers.faq", "/faq"),
            ("89ers.introduction", "/introduction"),
            ("89ers.order-history", "/order/history"),
            ("89ers.purcharsed-credit", "/purcharsed/credit"),
            ("89ers.purchased-seven", "/purcharsed/seven"),
            ("89ers.tickets_top", "/tickets/top"),
            ]
        self.page_doubles = page_doubles
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
                             url=url)\
                      for name, url in self.page_doubles]
        result = Result(retval, build_dict(retval, "name"))
        return result

    @reify
    def build_page(self):       
        layouts = self.build_layout.cache
        retval = [self.Datum("page", 
                  name=pageset.name, 
                  title=pageset.name, 
                  url=pageset.url, 
                  description="", 
                  pageset=t.many_to_one(pageset, "pageset_id"), 
                  keywords="", 
                  published=True, 
                  publish_begin=self.Default.publish_begin, 
                  created_at=self.Default.created_at, 
                  updated_at=self.Default.updated_at, 
                  organization_id=self.organization_id, 
                  layout_id=layouts[pageset.name])
                      for pageset in self.build_pageset]
        result = Result(retval, build_dict(retval, "name"))
        return result
        
    def build(self):
        return itertools.chain.from_iterable([
                self.build_layout, 
                self.build_pageset, 
                self.build_page
                ], )
                 

class WithOffsetSqlBuilder(SQLBuilder):
    """ insert sql id with offset value

    e.g. offset = 10
    insert statment start from id=11
    """
    def __init__(self, *args, **kwargs):
        super(WithOffsetSqlBuilder, self).__init__(*args, **kwargs)
        self.offset_table = {}

        self.session = sqlahelper.get_session()
        self.table_to_declarative = self.collect_declarative(sqlahelper.get_base())

    def collect_declarative(self, base):
        table_to_declarative = {}
        if base is not None:
            for class_name, declarative in base._decl_class_registry.items():
                table_to_declarative[declarative.__table__.name] = declarative
        return table_to_declarative
        

    def _get_offset_value(self, schema):
        cls = self.table_to_declarative[schema]
        return cls.query.with_entities(sa.func.Max(cls.id)).scalar() or 0

    def get_offset_value(self, schema): #memoize function
        if not schema in self.offset_table:
            self.offset_table[schema] = self._get_offset_value(schema)
        return self.offset_table[schema]
        
    def insert(self, table, data):

        assert data
        assert data[0][0] == "id"

        data[0] = data[0][0], data[0][1] + self.get_offset_value(table)
        super(WithOffsetSqlBuilder, self).insert(table, data)

Base = sqlahelper.get_base()
Session = sqlahelper.get_session()
Datum = newSADatum(Base.metadata, Base)

builder = Bj89ersFixtureBuilder(Datum)
suite = DataSuite()
walker = DataWalker(suite)

for datum in builder.build():
    walker(datum)
SQLGenerator(sys.stdout, encoding='utf-8', builder_impl=WithOffsetSqlBuilder)(suite)
