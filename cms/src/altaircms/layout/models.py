# coding: utf-8
from datetime import datetime
from altaircms.models import DBSession
from sqlalchemy import Column, Integer, DateTime, Unicode, String, ForeignKey
from altaircms.models import Base, BaseOriginalMixin

class Layout(BaseOriginalMixin, Base):
    """
    テンプレートレイアウトマスタ
    """
    query = DBSession.query_property()
    __tablename__ = "layout"

    id = Column(Integer(), primary_key=True)
    created_at = Column(DateTime(), default=datetime.now())
    updated_at = Column(DateTime(), default=datetime.now())

    title = Column(String())
    template_filename = Column(String())
    DEFAULT_BLOCKS = "[]"
    blocks = Column(String(), default=DEFAULT_BLOCKS)

    site_id = Column(Integer(), ForeignKey("site.id"))
    client_id = Column(Integer(), ForeignKey("client.id"))

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self.template_filename)
