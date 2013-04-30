# coding: utf-8
import json
import os
from datetime import datetime
from altaircms.models import DBSession
from sqlalchemy import Column, Integer, DateTime, Unicode, String, ForeignKey, Text
import sqlalchemy as sa
import sqlalchemy.orm as orm
from altaircms.models import Base, BaseOriginalMixin
from altaircms.models import WithOrganizationMixin
from altaircms.auth.models import Organization
from altaircms.widget.models import WidgetDisposition

class Layout(BaseOriginalMixin, WithOrganizationMixin, Base):
    """
    テンプレートレイアウトマスタ
    """
    query = DBSession.query_property()
    __tablename__ = "layout"

    id = Column(Integer(), primary_key=True)
    created_at = Column(DateTime(), default=datetime.now())
    updated_at = Column(DateTime(), default=datetime.now())
    uploaded_at = Column(DateTime())
    file_url = Column(String(255))
    title = Column(String(255))
    template_filename = Column(String(255))
    DEFAULT_BLOCKS = "[]"
    blocks = Column(Text, default=DEFAULT_BLOCKS)

    pagetype_id = Column(sa.Integer, ForeignKey("pagetype.id"))
    pagetype = orm.relationship("PageType", backref="layouts", uselist=False)
    disposition_id = sa.Column(sa.Integer, sa.ForeignKey("widgetdisposition.id", use_alter=True, name="fk_default_disposition"),doc=u"default settings")
    default_disposition = orm.relationship(WidgetDisposition, uselist=False, primaryjoin="WidgetDisposition.id==Layout.disposition_id")

    @classmethod
    def applicable(cls, pagetype_id):
        def transformation(qs):
            return qs.filter(sa.or_(Layout.pagetype_id==pagetype_id, Layout.pagetype_id==None))
        return transformation

    @property
    def organization(self):
        if self.organization_id is None:
            return None
        return Organization.query.filter_by(id=self.organization_id).first()

    @property
    def prefixed_template_filename(self):
        return os.path.join(self.organization.short_name, self.template_filename)

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

    @property
    def dependencies(self):
        return [self.prefixed_template_filename]
