# coding: utf-8
"""
ウィジェット用のモデルを定義する。

設定が必要なウィジェットのみ情報を保持する。
"""

import sqlalchemy as sa
import sqlalchemy.orm as orm

from altaircms.models import Base, DBSession

from datetime import datetime
from zope.interface import implements
from altaircms.interfaces import IHasSite
from altaircms.interfaces import IHasTimeHistory


__all__ = [
    'Widget',
]

WIDGET_TYPE = [
    'text',
    'breadcrumbs',
    'flash',
    'movie',
    'image',
    'topic',
    'menu',
    'billinghistory',
]

class Widget(Base):
    implements(IHasTimeHistory, IHasSite)

    query = DBSession.query_property()
    __tablename__ = "widget"
    page_id = sa.Column(sa.Integer, sa.ForeignKey("page.id"))
    page = orm.relationship("Page", backref="widgets", single_parent = True)
    id = sa.Column(sa.Integer, primary_key=True)
    site_id = sa.Column(sa.Integer, sa.ForeignKey("site.id"))
    discriminator = sa.Column("type", sa.String(32), nullable=False)
    created_at = sa.Column(sa.DateTime, default=datetime.now())
    updated_at = sa.Column(sa.DateTime, default=datetime.now())

    __mapper_args__ = {"polymorphic_on": discriminator}

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self.id)

    def clone(self, session, page):
        D = self.to_dict()
        D["id"] = None
        D["page_id"] = None
        D["page"] = None
        ins = self.__class__.from_dict(D)
        session.add(ins)
        return ins


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

