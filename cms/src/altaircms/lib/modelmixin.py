# -*- coding:utf-8 -*-

import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.declarative import declared_attr
from datetime import datetime

class AboutPublishMixin(object):
    """ 表示順序を定義可能なmodelが持つ
    """
    publish_open_on = sa.Column(sa.DateTime)
    publish_close_on = sa.Column(sa.DateTime)
    orderno = sa.Column(sa.Integer, default=50)
    is_vetoed = sa.Column(sa.Boolean, default=False)
    
    @classmethod
    def publishing(cls, d=None, qs=None):
        if d is None:
            d = datetime.now()
        if qs is None:
            qs = cls.query
        return cls._has_permissions(cls._orderby_logic(cls._publishing(qs, d)))

    @classmethod
    def _has_permissions(cls, qs):
        """ 公開可能なもののみ
        """
        return qs.filter(cls.is_vetoed==False)

    @classmethod
    def _publishing(cls, qs, d):
        """ 掲載期間のもののみ
        """
        qs = qs.filter(cls.publish_open_on  <= d)
        return qs.filter(d <= cls.publish_close_on)

    @classmethod
    def _orderby_logic(cls, qs):
        """ 表示順序で並べた後、公開期間で降順
        """
        table = cls.__tablename__
        return qs.order_by(sa.asc(table+".orderno"),
                           sa.desc(table+".publish_open_on"), 
                           )


