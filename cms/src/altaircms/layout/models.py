# coding: utf-8
from datetime import datetime

from sqlalchemy import Column, Integer, DateTime, Unicode, String, ForeignKey
from altaircms.models import Base

class Layout(Base):
    """
    テンプレートレイアウトマスタ
    """
    __tablename__ = "layout"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now())

    title = Column(Unicode)
    template_filename = Column(String)

    site_id = Column(Integer, ForeignKey("site.id"))
    client_id = Column(Integer, ForeignKey("client.id"))
