# -*- coding:utf-8 -*-

import sqlalchemy as sa
import sqlalchemy.orm as orm
from altaircms.models import Base
from altaircms.models import DBSession

import altaircms.helpers as h

class Category(Base):
    """
    サイト内カテゴリマスター

    hierarychy:   大      中     小
    　　　　　　  音楽
    　　　　　　　　　　　邦楽
                                  ポップス・ロック（邦楽）

                  スポーツ
　　　　　　　　　　　　　野球
　　　　　　　　　　　　　　　　　プロ野球
　　　　　　　　　演劇
　　　　　　　　　　　　　ミュージカル
                                  劇団四季
                  イベント(? static page)

    ※ このオブジェクトは、対応するページへのリンクを持つ(これはCMSで生成されないページへのリンクで有る場合もある)
    """
    __tablename__ = "category"
    __tableargs__ = (
        sa.UniqueConstraint("site_id", "name")
        )
    query = DBSession.query_property()
    id = sa.Column(sa.Integer, primary_key=True)

    site_id = sa.Column(sa.Integer, sa.ForeignKey("site.id"))
    parent_id = sa.Column(sa.Integer, sa.ForeignKey("category"))
    parent = orm.relationship("Parent", backref="children", primaryjoin="Parent.id == Parent.parent_id")

    name = sa.Column(sa.Unicode(length=255), nullable=False)
    hierarchy = sa.Column(sa.Unicode(length=255), nullable=False)
    
    url = sa.Column(sa.Unicode(length=255))
    pageset_id = sa.Column(sa.Integer, sa.ForeignKey("pagesets.id"))
    pagesest = orm.relationship("PageSet", backref="category", uselist=False)
    
    def get_link(self, request):
        if self.pageset is None:
            return self.url
        else:
            return h.front.to_publish_page_from_pageset(request, self.pageset)
    
