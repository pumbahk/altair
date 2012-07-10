# coding: utf-8
"""
ウィジェット用のベースモデルを定義する。

"""
import json
import sqlalchemy as sa
import sqlalchemy.orm as orm

from altaircms.models import Base, DBSession, BaseOriginalMixin
from altaircms.models import WithOrganizationMixin

from datetime import datetime
from zope.interface import implements
from altaircms.page.models import Page
from altaircms.layout.models import Layout

from altaircms.widget.tree.proxy import WidgetTreeProxy
import altaircms.widget.tree.clone as wclone


__all__ = [
    'Widget',
    "WidgetDisposition", 
    "AssetWidgetResourceMixin"
]

class Widget(BaseOriginalMixin, Base):
    query = DBSession.query_property()
    __tablename__ = "widget"
    page_id = sa.Column(sa.Integer, sa.ForeignKey("page.id"))
    page = orm.relationship("Page", backref="widgets")

    disposition_id = sa.Column(sa.Integer, sa.ForeignKey("widgetdisposition.id"))
    disposition = orm.relationship("WidgetDisposition", backref="widgets")

    id = sa.Column(sa.Integer, primary_key=True)
    discriminator = sa.Column("type", sa.String(32), nullable=False)
    created_at = sa.Column(sa.DateTime, default=datetime.now)
    updated_at = sa.Column(sa.DateTime, default=datetime.now, onupdate=datetime.now)

    __mapper_args__ = {"polymorphic_on": discriminator}

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self.id)

    def clone(self, session, page=None): #todo:refactoring model#clone
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

class WidgetDisposition(WithOrganizationMixin, BaseOriginalMixin, Base): #todo: rename
    """ widgetの利用内容を記録しておくためのモデル
    以下を記録する。
    * 利用しているwidgetの位置
    * 利用しているwidgetのデータ

    pageから作成し、pageにbindする
    """
    query = DBSession.query_property()
    __tablename__ = "widgetdisposition"
    id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.Unicode(255))

    structure = sa.Column(sa.Text, default=Page.DEFAULT_STRUCTURE) # same as: Page.structure
    blocks = sa.Column(sa.String(255), default=Layout.DEFAULT_BLOCKS) # same as: Layout.blocks

    is_public = sa.Column(sa.Boolean, default=False)
    owner_id = sa.Column(sa.Integer, sa.ForeignKey("operator.id"))
    owner = orm.relationship("Operator", backref="widget_dispositions")
    created_at = sa.Column(sa.DateTime, default=datetime.now)
    updated_at = sa.Column(sa.DateTime, default=datetime.now, onupdate=datetime.now)
    
    @classmethod
    def _create_empty_from_page(cls, page, title_fmt=u"%sより"):
        D = {"title": title_fmt % page.title, 
             "organization_id": page.organization_id, 
             "blocks": page.layout.blocks}
        return cls.from_dict(D)

    @classmethod
    def from_page(cls, page, session):
        wtree = WidgetTreeProxy(page)
        new_wtree = wclone.clone(session, None, wtree)
        if session:
            session.flush()
        new_structure = wclone.to_structure(new_wtree)

        instance = cls._create_empty_from_page(page, title_fmt=u"%sより") ##
        instance.structure = json.dumps(new_structure)
        for k, ws in new_wtree.blocks.iteritems():
            for w in ws:
                w.disposition = instance
        return instance

    def bind_page(self, page, session):
        ## cleanup
        wtree = WidgetTreeProxy(self)
        new_wtree = wclone.clone(session, page, wtree)

        for w in page.widgets:
            assert w.page

        if session:
            session.flush()
        page.structure = json.dumps(wclone.to_structure(new_wtree))
        return page

    def delete_widgets(self):
        where = (Widget.disposition_id==self.id) & (Widget.page==None)
        for w in Widget.query.filter(where):
            DBSession.delete(w)


    @classmethod
    def _snapshot_title(cls):
        return u"%%s(%s)" % str(datetime.now())

    @classmethod
    def snapshot(cls, page, owner, session):
        """ move widgets page to widget disposition(as tmpstorage)
        """
        dispos = cls._create_empty_from_page(page, title_fmt=cls._snapshot_title()) ##
        dispos.structure = page.structure
        dispos.owner = owner
        page.structure = Page.DEFAULT_STRUCTURE
        if session:
            session.add(page)
            session.add(dispos)
        Widget.query.filter(Widget.page==page).update(
            {Widget.page: None,  Widget.disposition:dispos}
            )
        return dispos

    @classmethod
    def same_blocks_query(cls, page):
        return cls.query.filter(cls.blocks==page.layout.blocks)

    @classmethod
    def enable_only_query(cls, operator, qs=None):
        return (qs or cls.query).filter((cls.is_public==True)|(cls.owner==operator))

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
        return self.request.allowable(self.AssetClass)

    def get_asset(self, asset_id):
        return self.request.allowable(self.AssetClass).filter(self.AssetClass.id == asset_id).one()

