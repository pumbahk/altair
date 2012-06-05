# -*- encoding:utf-8 -*-

"""add initial pagesets categorytop

Revision ID: 126c50f99cd7
Revises: 513581379efc
Create Date: 2012-06-05 10:19:42.085505

"""

# revision identifiers, used by Alembic.
revision = '126c50f99cd7'
down_revision = '513581379efc'

from alembic import op
import sqlalchemy as sa

"""
pageset_default_info - pageset - categoryを作成する
category,  pagesetは再帰的
"""

from altaircms.page.models import PageDefaultInfo
from altaircms.page.models import PageSet
from altaircms.page.models import Page
from altaircms.models import Category, Site
from functools import partial
import transaction

"""
一度きりのfactoryなのでinstance作らない. class=instance
"""

import pkg_resources
def import_symbol(symbol):
    return pkg_resources.EntryPoint.parse("x=%s" % symbol).load(False)

def merged(defaults, **kwargs):
    D = defaults.copy()
    D.update(kwargs)
    return D

def with_session(session, o):
    session.add(o)
    return o 

def generate_from_tabular(fn, headings, tabular):
    return [fn(**dict(zip(headings, line))) for line in tabular]

def create_child(page_default_info, name, category, url=None, url_fmt=None, title_fmt=None):
    page = page_default_info.create_page(name, url=url, category=category)

    child = page_default_info.clone_with_pageset(page.pageset,
                                   title_fmt=title_fmt or page_default_info.title_fmt, 
                                   url_fmt=url_fmt or page_default_info.url_fmt)
    return child


from altaircms.models import DBSession

def O(o):
    DBSession.add(o)
    return o


def upgrade():
    site = Site.query.filter_by(name=u"ticketstar").one()

    keywords = u"チケット,演劇,クラシック,オペラ,コンサート,バレエ,ミュージカル,野球,サッカー,格闘技"
    description=u"チケットの販売、イベントの予約は楽天チケットで！楽天チケットは演劇、バレエ、ミュージカルなどの舞台、クラシック、オペラ、ロックなどのコンサート、野球、サッカー、格闘技などのスポーツ、その他イベントなどのチケットのオンラインショッピングサイトです。"
    title_fmt = u"【楽天チケット】%(title)s｜公演・ライブのチケット予約・購入"

    ### top
    root = Category.query.filter_by(label=u"チケットトップ").one()

    top_level_pdi = PageDefaultInfo(keywords=keywords, 
                                    description=description, 
                                    url_fmt="/",
                                    title_fmt = u"【楽天チケット】%(title)s｜公演・ライブのチケット予約・購入")
    O(top_level_pdi.create_page(u"トップ", category=root))





    ### music
    root = Category.query.filter_by(label=u"音楽").one()

    top_level_pdi = O(PageDefaultInfo(keywords=keywords, 
                                    description=description,
                                    url_fmt=u"/s/%(url)s", 
                                    title_fmt=title_fmt))
    category_page = O(top_level_pdi.create_page(u"音楽", url=u"music", category=root))
    

    pdi = top_level_pdi.clone_with_pageset(category_page.pageset, 
                                           url_fmt=u"/%s/%%(url)s" % category_page.pageset.name, 
                                           title_fmt=title_fmt)
    
    subcategory_create = partial(Category, site=site, hierarchy=u"中", parent=root)
    headings = ["name", "label"]
    tabular = import_symbol("altaircms.seeds.categories.music:MUSIC_SUBCATEGORY_CHOICES")

    categories = generate_from_tabular(subcategory_create, headings, tabular)

    for category in categories:
        O(create_child(pdi, category.label, category, url_fmt="u/%s/%%(url)s" % category.label))





    ### sports
    root = Category.query.filter_by(label=u"スポーツ").one()

    top_level_pdi = O(PageDefaultInfo(keywords=keywords, 
                                    description=description,
                                    url_fmt=u"/s/%(url)s", 
                                    title_fmt=title_fmt))
    category_page = O(top_level_pdi.create_page(u"スポーツ", url=u"sports", category=root))
    

    pdi = top_level_pdi.clone_with_pageset(category_page.pageset, 
                                           url_fmt=u"/%s/%%(url)s" % category_page.pageset.name, 
                                           title_fmt=title_fmt)
    
    subcategory_create = partial(Category, site=site, hierarchy=u"中", parent=root)
    headings = ["name", "label"]
    tabular = import_symbol("altaircms.seeds.categories.sports:SPORTS_SUBCATEGORY_CHOICES")

    categories = generate_from_tabular(subcategory_create, headings, tabular)

    for category in categories:
        O(create_child(pdi, category.label, category, url_fmt="u/%s/%%(url)s" % category.label))




    ### stage

    root = Category.query.filter_by(label=u"演劇").one()

    top_level_pdi = O(PageDefaultInfo(keywords=keywords, 
                                    description=description,
                                    url_fmt=u"/s/%(url)s", 
                                    title_fmt=title_fmt))
    category_page = O(top_level_pdi.create_page(u"演劇", url=u"stage", category=root))
    

    pdi = top_level_pdi.clone_with_pageset(category_page.pageset, 
                                           url_fmt=u"/%s/%%(url)s" % category_page.pageset.name, 
                                           title_fmt=title_fmt)
    
    subcategory_create = partial(Category, site=site, hierarchy=u"中", parent=root)
    headings = ["name", "label"]
    tabular = import_symbol("altaircms.seeds.categories.stage:STAGE_SUBCATEGORY_CHOICES")

    categories = generate_from_tabular(subcategory_create, headings, tabular)

    for category in categories:
        O(create_child(pdi, category.label, category, url_fmt="u/%s/%%(url)s" % category.label))




    ### other

    root = Category.query.filter_by(label=u"イベント・その他").one()

    top_level_pdi = O(PageDefaultInfo(keywords=keywords, 
                                    description=description,
                                    url_fmt=u"/s/%(url)s", 
                                    title_fmt=title_fmt))
    category_page = O(top_level_pdi.create_page(u"イベント・その他", url=u"other", category=root))
    

    pdi = top_level_pdi.clone_with_pageset(category_page.pageset, 
                                           url_fmt=u"/%s/%%(url)s" % category_page.pageset.name, 
                                           title_fmt=title_fmt)
    
    subcategory_create = partial(Category, site=site, hierarchy=u"中", parent=root)
    headings = ["name", "label"]
    tabular = import_symbol("altaircms.seeds.categories.other:OTHER_SUBCATEGORY_CHOICES")

    categories = generate_from_tabular(subcategory_create, headings, tabular)

    for category in categories:
        O(create_child(pdi, category.label, category, url_fmt="u/%s/%%(url)s" % category.label))


    transaction.commit()


def downgrade():
    op.execute("""
SET FOREIGN_KEY_CHECKS = 0;
delete from category;
delete from page;
delete from pagesets;
SET FOREIGN_KEY_CHECKS = 1;
""")

