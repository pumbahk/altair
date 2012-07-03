# coding: utf-8
import json
from datetime import datetime
from altaircms.models import DBSession
from sqlalchemy import Column, Integer, DateTime, Unicode, String, ForeignKey, Text
import sqlalchemy as sa
import sqlalchemy.orm as orm
from altaircms.models import Base, BaseOriginalMixin
from altaircms.models import WithOrganizationMixin

class Layout(BaseOriginalMixin, WithOrganizationMixin, Base):
    """
    テンプレートレイアウトマスタ
    """
    query = DBSession.query_property()
    __tablename__ = "layout"

    id = Column(Integer(), primary_key=True)
    created_at = Column(DateTime(), default=datetime.now())
    updated_at = Column(DateTime(), default=datetime.now())

    title = Column(String(255))
    template_filename = Column(String(255))
    DEFAULT_BLOCKS = "[]"
    blocks = Column(Text, default=DEFAULT_BLOCKS)

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self.template_filename)

    def valid_block(self):
        """ 保存されているjsonのデータがparseできるものか調べる。
        (performanceが気になったらloadsされたオブジェクトの再利用を考える)
        """
        try:
            json.loads(self.blocks)
        except ValueError:
            return False
        return True
            
            
