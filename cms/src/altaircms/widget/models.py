# coding: utf-8
"""
ウィジェット用のベースモデルを定義する。

"""
import json
import sqlalchemy as sa
import sqlalchemy.orm as orm

from altaircms.models import Base, DBSession

from datetime import datetime
from zope.interface import implements
from altaircms.interfaces import IHasSite
from altaircms.interfaces import IHasTimeHistory

__all__ = [
    'Widget',
    "WidgetDisposition", 
    "AssetWidgetResourceMixin"
]

class Widget(Base):
    implements(IHasTimeHistory, IHasSite)

    query = DBSession.query_property()
    __tablename__ = "widget"
    page_id = sa.Column(sa.Integer, sa.ForeignKey("page.id"))
    page = orm.relationship("Page", backref="widgets")
    # page = orm.relationship("Page", backref="widgets", single_parent = True)

    disposition_id = sa.Column(sa.Integer, sa.ForeignKey("widgetdisposition.id"))
    disposition = orm.relationship("WidgetDisposition", backref="widgets")

    id = sa.Column(sa.Integer, primary_key=True)
    site_id = sa.Column(sa.Integer, sa.ForeignKey("site.id"))
    discriminator = sa.Column("type", sa.String(32), nullable=False)
    created_at = sa.Column(sa.DateTime, default=datetime.now)
    updated_at = sa.Column(sa.DateTime, default=datetime.now, onupdate=datetime.now)

    __mapper_args__ = {"polymorphic_on": discriminator}

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self.id)

    def clone(self, session, page): #todo:refactoring model#clone
        D = self.to_dict()
        D["id"] = None
        if page:
            D["page_id"] = page.id
            D["page"] = page
        else:
            D["page_id"] = D["page"] = None
        ins = self.__class__.from_dict(D)
        session.add(ins)
        return ins


class WidgetDisposition(Base): #todo: rename
    """ widgetの利用内容を記録しておくためのモデル
    以下を記録する。
    * 利用しているwidgetの位置
    * 利用しているwidgetのデータ

    pageから作成し、pageにbindする
    """
    implements(IHasTimeHistory, IHasSite)
    
    query = DBSession.query_property()
    __tablename__ = "widgetdisposition"
    id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.Unicode(255))
    site_id = sa.Column(sa.Integer, sa.ForeignKey("site.id"))

    structure = sa.Column(sa.String) # same as: Page.structure
    blocks = sa.Column(sa.String) # same as: Layout.blocks

    is_public = sa.Column(sa.Boolean, default=False)
    owner_id = sa.Column(sa.Integer, sa.ForeignKey("operator.id"))
    owner = orm.relationship("Operator", backref="widget_dispositions")
    created_at = sa.Column(sa.DateTime, default=datetime.now)
    updated_at = sa.Column(sa.DateTime, default=datetime.now, onupdate=datetime.now)
    
    @classmethod
    def from_page(cls, page, session):
        from altaircms.widget.tree.proxy import WidgetTreeProxy
        import altaircms.widget.tree.clone as wclone
        wtree = WidgetTreeProxy(page)
        new_wtree = wclone.clone(session, None, wtree)
        if session:
            session.flush()
        new_structure = wclone.to_structure(new_wtree)

        D = {"structure": json.dumps(new_structure), 
             "title": u"%sより" % page.title, 
             "site_id": page.site_id, 
             "blocks": page.layout.blocks}

        instance = cls.from_dict(D)
        for k, ws in new_wtree.blocks.iteritems():
            for w in ws:
                w.disposition = instance
        return instance

    def bind_page(self, page, session):
        from altaircms.widget.tree.proxy import WidgetTreeProxy
        import altaircms.widget.tree.clone as wclone
        wtree = WidgetTreeProxy(self)
        new_wtree = wclone.clone(session, page, wtree)
        # if session:
        #     session.flush()
        page.structure = json.dumps(wclone.to_structure(new_wtree))
        return page

    ## todo:fixme
    def delete_widgets(self):
        where = (Widget.disposition_id==self.id) & (Widget.page_id==None)
        DBSession.query(Widget.id).filter(where).delete()

    @classmethod
    def same_blocks_query(cls, page):
        return cls.query.filter(cls.blocks==page.layout.blocks)

    @classmethod
    def enable_only_query(cls, operator):
        return cls.query.filter((cls.is_public==True)|(cls.owner==operator))

    def __repr__(self):
        return self.title

class AssetWidgetResourceMixin(object):
    WidgetClass = None
    AssetClass = None

    def _get_or_create(self, model, widget_id):
        if widget_id is None:
            return model()
        else:
            return DBSession.query(model).filter(model.id == widget_id).one()
        
    def get_widget(self, widget_id):
        return self._get_or_create(self.WidgetClass, widget_id)

    def get_asset_query(self):
        return self.AssetClass.query

    def get_asset(self, asset_id):
        return self.AssetClass.query.filter(self.AssetClass.id == asset_id).one()

