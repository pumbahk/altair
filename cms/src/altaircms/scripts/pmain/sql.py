# -*- coding:utf-8 -*-
from altaircms.models import Category
from altaircms.page.models import PageSet
from altaircms.models import DBSession
from sqlalchemy.orm import aliased

"""
親カテゴリからがmusicである。中カテゴリを盗る
"""
def main(*args, **kwargs):
    import pdb; pdb.set_trace()
    sub_stmt = DBSession.query(Category.id).filter_by(name="music").subquery()
    parents_ids =  aliased(Category, sub_stmt)

    sub_stmt = Category.query.join(parents_ids, parents_ids.id==Category.parent_id).subquery()
    categories = aliased(Category, sub_stmt)
    
    sub_stmt = PageSet.query.join(categories, categories.pageset_id==PageSet.id).subquery()
    parent_pagesets = aliased(PageSet, sub_stmt)

    qs = PageSet.query.join(parent_pagesets, PageSet.parent_id==parent_pagesets.id).all()
    
def main(*args, **kwargs):
    names = ["music"]
    parent_category_ids = DBSession.query(Category.id).filter(Category.name.in_(names))
    category_ids = DBSession.query(Category.id).filter(Category.parent_id.in_(parent_category_ids))
    parent_ids = DBSession.query(PageSet.id).filter(PageSet.id.in_(category_ids))
    PageSet.query.filter(PageSet.parent_id.in_(parent_ids)).all()

def main(*args, **kwargs):
    """ pageset category は1:1なのでjoinしてしまったほうが 良いかも
    Category -> (Category * PageSet) -> PageSet 
    """
    names = ["music"]
    parent_category_ids = DBSession.query(Category.id).filter(Category.name.in_(names))
    category_page_ids = DBSession.query(PageSet.id).join(Category, PageSet.id==Category.pageset_id).filter(Category.parent_id.in_(parent_category_ids))
    PageSet.query.filter(PageSet.parent_id.in_(category_page_ids)).all()

 
