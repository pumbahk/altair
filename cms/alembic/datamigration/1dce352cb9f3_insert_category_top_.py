# -*- encoding:utf-8 -*-

"""insert category-top-page

Revision ID: 1dce352cb9f3
Revises: a47ddbeb352
Create Date: 2012-06-08 17:16:08.192107

"""

# revision identifiers, used by Alembic.
revision = '1dce352cb9f3'
down_revision = 'a47ddbeb352'


from alembic import op
import sqlalchemy as sa


"""
pageset_default_info - pageset - categoryを作成する
category,  pagesetは再帰的
"""

from altaircms.page.models import PageDefaultInfo
from altaircms.models import Category
from altaircms.auth.models import Organization
from altaircms.layout.models import Layout
from functools import partial
import transaction

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

def create_master_categories(organization_id):
   
   ## トップページ
    DBSession.add(Category(organization_id=organization_id, hierarchy=u"大", label=u"チケットトップ", name="index", orderno=0, 
                              imgsrc="/static/ticketstar/img/common/header_nav_top.gif"))
    ## 音楽
    DBSession.add(Category(organization_id=organization_id, hierarchy=u"大", label=u"音楽", name="music", orderno=1, 
                              imgsrc="/static/ticketstar/img/common/header_nav_music.gif"))

    DBSession.add(Category(organization_id=organization_id, hierarchy=u"大", label=u"スポーツ", name="sports", orderno=2, 
                              imgsrc="/static/ticketstar/img/common/header_nav_sports.gif"))

    DBSession.add(Category(organization_id=organization_id, hierarchy=u"大", label=u"演劇", name="stage", orderno=3, 
                              imgsrc="/static/ticketstar/img/common/header_nav_stage.gif"))
    
    DBSession.add(Category(organization_id=organization_id, hierarchy=u"大", label=u"イベント・その他", name="event", orderno=4, 
                              imgsrc="/static/ticketstar/img/common/header_nav_event.gif"))

    ## misc global navigation
    DBSession.add(Category(organization_id=organization_id, orderno=1, hierarchy=u"top_outer", url="http://example.com", label=u"初めての方へ", name="first"))
    DBSession.add(Category(organization_id=organization_id, orderno=2, hierarchy=u"top_outer", url="http://example.com", label=u"公演中止・変更情報", name="change"))
    DBSession.add(Category(organization_id=organization_id, orderno=3, hierarchy=u"top_outer", url="http://example.com", label=u"ヘルプ", name="help"))
    DBSession.add(Category(organization_id=organization_id, orderno=4, hierarchy=u"top_outer", url="http://example.com", label=u"サイトマップ", name="organization_idmap"))

    DBSession.add(Category(organization_id=organization_id, orderno=1, hierarchy=u"top_inner", url="http://example.com", label=u"マイページ", name="mypage"))
    DBSession.add(Category(organization_id=organization_id, orderno=2, hierarchy=u"top_inner", url="http://example.com", label=u"お気に入り", name="favorite"))
    DBSession.add(Category(organization_id=organization_id, orderno=3, hierarchy=u"top_inner", url="http://example.com", label=u"購入履歴", name="purchase_history"))
    DBSession.add(Category(organization_id=organization_id, orderno=4, hierarchy=u"top_inner", url="http://example.com", label=u"抽選申込履歴", name="lottery_history"))

def create_child(page_default_info, name, category, url=None, url_fmt=None, title_fmt=None):
    """ 子のpageset, page, page_default_infoを作成
    """
    page = page_default_info.create_page(name, url=url, category=category)

    ## 親ページの名前も追加するように変更
    ## ポップス -> 音楽 ポップス
    parent = getattr(category.pageset, "parent", None)
    if parent:
        page.name = u"%s %s" % (parent.name ,  page.name)
        page.pageset.name = u"%s %s" % (parent.name ,  page.pageset.name)

    child = page_default_info.clone_with_pageset(page.pageset,
                                   title_fmt=title_fmt or page_default_info.title_fmt, 
                                   url_fmt=url_fmt or page_default_info.url_fmt)
    return child


from altaircms.models import DBSession

def O(o):
    DBSession.add(o)
    return o

def get_layout(filename):
    return Layout.query.filter_by(template_filename=filename).one()


def create_category_top_page(organization_id):
    keywords = u"チケット,演劇,クラシック,オペラ,コンサート,バレエ,ミュージカル,野球,サッカー,格闘技"
    description=u"チケットの販売、イベントの予約は楽天チケットで！楽天チケットは演劇、バレエ、ミュージカルなどの舞台、クラシック、オペラ、ロックなどのコンサート、野球、サッカー、格闘技などのスポーツ、その他イベントなどのチケットのオンラインショッピングサイトです。"
    title_fmt = u"【楽天チケット】%(title)s｜公演・ライブのチケット予約・購入"

    ### top
    root = Category.query.filter_by(label=u"チケットトップ").one()

    top_level_pdi = PageDefaultInfo(keywords=keywords, 
                                    description=description, 
                                    url_fmt="",
                                    title_fmt = u"【楽天チケット】%(title)s｜公演・ライブのチケット予約・購入"
                                    )
    top_page = O(top_level_pdi.create_page(u"トップページ", category=root, layout=get_layout("ticketstar.top.mako")))
    top_level_pdi.pageset = top_page.pageset
    





    ### music
    root = Category.query.filter_by(label=u"音楽").one()

    top_level_pdi = O(PageDefaultInfo(keywords=keywords, 
                                      description=description,
                                      url_fmt=u"%(url)s", 
                                      title_fmt=title_fmt))
    category_page = O(top_level_pdi.create_page(u"音楽", url=u"music", category=root, layout=get_layout("ticketstar.music.mako")))



    pdi = top_level_pdi.clone_with_pageset(category_page.pageset, 
                                           url_fmt=u"s/%s/%%(url)s" % top_level_pdi._url(root.label), 
                                           title_fmt=title_fmt)
    
    subcategory_create = partial(Category, organization_id=organization_id, hierarchy=u"中", parent=root)
    headings = ["name", "label"]
    tabular = import_symbol("altaircms.seeds.categories.music:MUSIC_SUBCATEGORY_CHOICES")

    categories = generate_from_tabular(subcategory_create, headings, tabular)

    for category in categories:
        O(create_child(pdi, category.label, category, url_fmt=u"%s/%%(url)s" % pdi._url(category.label)))





    ### sports
    root = Category.query.filter_by(label=u"スポーツ").one()

    top_level_pdi = O(PageDefaultInfo(keywords=keywords, 
                                      description=description,
                                      url_fmt=u"%(url)s", 
                                      title_fmt=title_fmt))
    category_page = O(top_level_pdi.create_page(u"スポーツ", url=u"sports", category=root, layout=get_layout("ticketstar.sports.mako")))


    pdi = top_level_pdi.clone_with_pageset(category_page.pageset, 
                                           url_fmt=u"s/%s/%%(url)s" % top_level_pdi._url(root.label), 
                                           title_fmt=title_fmt)
    
    subcategory_create = partial(Category, organization_id=organization_id, hierarchy=u"中", parent=root)
    headings = ["name", "label"]
    tabular = import_symbol("altaircms.seeds.categories.sports:SPORTS_SUBCATEGORY_CHOICES")

    categories = generate_from_tabular(subcategory_create, headings, tabular)

    for category in categories:
        O(create_child(pdi, category.label, category, url_fmt=u"%s/%%(url)s" % pdi._url(category.label)))





    ### stage

    root = Category.query.filter_by(label=u"演劇").one()

    top_level_pdi = O(PageDefaultInfo(keywords=keywords, 
                                    description=description,
                                    url_fmt=u"%(url)s", 
                                    title_fmt=title_fmt))
    category_page = O(top_level_pdi.create_page(u"演劇", url=u"stage", category=root, layout=get_layout("ticketstar.stage.mako")))


    pdi = top_level_pdi.clone_with_pageset(category_page.pageset, 
                                           url_fmt=u"s/%s/%%(url)s" % top_level_pdi._url(root.label), 
                                           title_fmt=title_fmt)
    
    subcategory_create = partial(Category, organization_id=organization_id, hierarchy=u"中", parent=root)
    headings = ["name", "label"]
    tabular = import_symbol("altaircms.seeds.categories.stage:STAGE_SUBCATEGORY_CHOICES")

    categories = generate_from_tabular(subcategory_create, headings, tabular)

    for category in categories:
        O(create_child(pdi, category.label, category, url_fmt=u"%s/%%(url)s" % pdi._url(category.label)))





    ### other

    root = Category.query.filter_by(label=u"イベント・その他").one()

    top_level_pdi = O(PageDefaultInfo(keywords=keywords, 
                                    description=description,
                                    url_fmt=u"%(url)s", 
                                    title_fmt=title_fmt))
    category_page = O(top_level_pdi.create_page(u"イベント・その他", url=u"other", category=root, layout=get_layout("ticketstar.event.mako")))


    pdi = top_level_pdi.clone_with_pageset(category_page.pageset, 
                                           url_fmt=u"s/%s/%%(url)s" % top_level_pdi._url(root.label), 
                                           title_fmt=title_fmt)
    
    subcategory_create = partial(Category, organization_id=organization_id, hierarchy=u"中", parent=root)
    headings = ["name", "label"]
    tabular = import_symbol("altaircms.seeds.categories.other:OTHER_SUBCATEGORY_CHOICES")

    categories = generate_from_tabular(subcategory_create, headings, tabular)

    for category in categories:
        O(create_child(pdi, category.label, category, url_fmt=u"%s/%%(url)s" % pdi._url(category.label)))


def upgrade():
    organization_id = Organization.query.filter_by(name=u"master").one().id
    create_master_categories(organization_id)
    create_category_top_page(organization_id)
    transaction.commit()


def downgrade():
    def fk_activate(ltable, lcolname, rtable, rcolname, fkname):
        fmt = "ALTER TABLE %s ADD CONSTRAINT %s FOREIGN KEY (%s) REFERENCES %s(%s);"
        cmd = fmt % (ltable, fkname, lcolname, rtable, rcolname)
        op.execute(cmd)
        
    def fk_deactivate(table,  fkname):
        cmd = "ALTER TABLE %s DROP FOREIGN KEY %s;" % (table, fkname)
        op.execute(cmd)

    fk_deactivate("category", "fk_category_parent_id_to_category_id")
    fk_deactivate("pagesets", "fk_pagesets_parent_id_to_pagesets_id")
    fk_deactivate("page_default_info", "fk_page_default_info_pageset_id_to_pagesets_id")
    fk_deactivate("page", "fk_page_pageset_id_to_pagesets_id")


    op.execute("delete from category;")
    op.execute("delete from pagesets;")
    op.execute("delete from page;")
    op.execute("delete from page_default_info;")

    fk_activate("category", "parent_id", "category", "id", "fk_category_parent_id_to_category_id")
    fk_activate("pagesets", "parent_id", "pagesets", "id", "fk_pagesets_parent_id_to_pagesets_id")
    fk_activate("page", "pageset_id", "pagesets", "id", "fk_page_pageset_id_to_pagesets_id")
    fk_activate("page_default_info", "pageset_id", "pagesets", "id", "fk_page_default_info_pageset_id_to_pagesets_id")
