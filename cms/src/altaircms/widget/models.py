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
from collections import defaultdict
from zope.deprecation import deprecate
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

class StructureSaveType(object):
    shallow = "shallow"
    deep = "deep"

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

    DEFAULT_STRUCTURE="{}"
    structure = sa.Column(sa.Text, default=DEFAULT_STRUCTURE) # same as: Page.structure
    blocks = sa.Column(sa.String(255), default="[]") # same as: Layout.blocks #todo.remove
    layout_id = sa.Column(sa.Integer, sa.ForeignKey("layout.id"))
    layout = orm.relationship("Layout", uselist=False, primaryjoin="Layout.id==WidgetDisposition.layout_id")
    is_public = sa.Column(sa.Boolean, default=False)
    save_type = sa.Column(sa.String(16), index=True)
    owner_id = sa.Column(sa.Integer, sa.ForeignKey("operator.id"))
    owner = orm.relationship("Operator", backref="widget_dispositions")
    created_at = sa.Column(sa.DateTime, default=datetime.now)
    updated_at = sa.Column(sa.DateTime, default=datetime.now, onupdate=datetime.now)

    @deprecate("this is obsolute. use WidgetDisopositionLoader")    
    def bind_page(self, page, session=DBSession):
        loader = WidgetDispositionLoader(session)
        return loader.bind_page(self, page)

    @deprecate("this is obsolute. use WidgetDisopositionLoader")    
    def bind_page_shallow(self, page, session=DBSession):
        loader = WidgetDispositionLoader(session)
        return loader.bind_page_shallow(self, page)

    @deprecate("this is obsolute. use WidgetDisopositionLoader")    
    def bind_page_deep(self, page, session=DBSession):
        loader = WidgetDispositionLoader(session)
        return loader.bind_page_deep(self, page)

    def delete_widgets(self):
        where = (Widget.disposition_id==self.id) & (Widget.page==None)
        for w in Widget.query.filter(where):
            DBSession.delete(w)

    @classmethod
    @deprecate("this is obsolute. use WidgetDisopositionAllocator")
    def from_page(cls, page, session, save_type):
        allocator = WidgetDispositionAllocator(session)
        return allocator.disposition_from_page(page, save_type)

    @classmethod
    @deprecate("this is obsolute. use WidgetDisopositionAllocator")
    def shallow_copy_from_page(cls, page, session):
        allocator = WidgetDispositionAllocator(session)
        return allocator.shallow_copy_from_page(page)

    @classmethod
    @deprecate("this is obsolute. use WidgetDisopositionAllocator")
    def deep_copy_from_page(cls, page, session):
        allocator = WidgetDispositionAllocator(session)
        return allocator.deep_copy_from_page(page)

    @classmethod
    @deprecate("this is obsolute. use WidgetDisopositionAllocator")
    def snapshot(cls, page, owner, session):
        return WidgetDispositionAllocator(session).take_snapshot(page, owner)

    @classmethod
    def enable_only_query(cls, operator, qs=None):
        return (qs or cls.query).filter((cls.is_public==True)|(cls.owner==operator))

    def __repr__(self):
        return self.title

## todo rename
class WidgetDispositionLoader(object):
    def __init__(self, session=DBSession):
        self.session = session

    def bind_page(self, dispos, page):
        if dispos.save_type == StructureSaveType.shallow:
            return self.bind_page_shallow(dispos, page)
        elif dispos.save_type == StructureSaveType.deep:
            return self.bind_page_deep(dispos, page)
        else:
            raise NotImplementedError("save type %s is not implemented yet" % dispos.save_type)

    def bind_page_shallow(self, dispos, page):
        page.structure = dispos.structure
        return page

    def bind_page_deep(self, dispos, page):
        ## cleanup
        wtree = WidgetTreeProxy(dispos)
        new_wtree = wclone.clone(self.session, page, wtree)

        for w in page.widgets:
            assert w.page

        self.session.flush()
        page.structure = json.dumps(wclone.to_structure(new_wtree))
        return page
    
class WidgetDispositionAllocator(object):
    title_fmt = u"%sより"
    model = WidgetDisposition
    def __init__(self, session=DBSession):
        self.session = session

    def _snapshot_title(self):
        return u"%%s(%s)" % str(datetime.now())

    def take_snapshot(self, page, owner):
        """ move widgets page to widget disposition(as tmpstorage)
        """
        dispos =self.create_empty_from_page(page, title_fmt=self._snapshot_title()) ##
        dispos.structure = page.structure
        dispos.owner = owner
        page.structure = WidgetDisposition.DEFAULT_STRUCTURE
        self.session.add(page)
        self.session.add(dispos)
        Widget.query.filter(Widget.page==page).update(
            {Widget.page: None,  Widget.disposition:dispos}
            )
        return dispos

    def create_empty_from_page(self, page, title_fmt=u"%sより"):
        D = {"title": title_fmt % page.title, 
             "organization_id": page.organization_id, 
             "blocks": page.layout.blocks}
        return self.model.from_dict(D)


    def disposition_from_page(self, page, save_type):
        if save_type == StructureSaveType.deep:
            return self.deep_copy_from_page(page)
        elif save_type == StructureSaveType.shallow:
            return self.shallow_copy_from_page(page)
        else:
            raise NotImplementedError("save type %s is not implemented yet" % save_type)

    def shallow_copy_from_page(self, page):
        instance = self.create_empty_from_page(page, title_fmt=u"%sより") ##
        structure = json.loads(page.structure)
        new_structure = defaultdict(list)
        for k, vs in structure.iteritems():
            for v in vs:
                new_structure[k].append({"name": v["name"]})
        instance.structure = json.dumps(new_structure)
        instance.save_type = StructureSaveType.shallow
        instance.layout_id = page.layout_id
        return instance


    def deep_copy_from_page(self, page):
        wtree = WidgetTreeProxy(page)
        new_wtree = wclone.clone(self.session, None, wtree)
        self.session.flush()
        new_structure = wclone.to_structure(new_wtree)

        instance = self.create_empty_from_page(page, title_fmt=u"%sより") ##
        instance.structure = json.dumps(new_structure)
        instance.save_type = StructureSaveType.deep
        for k, ws in new_wtree.blocks.iteritems():
            for w in ws:
                w.disposition = instance
        instance.layout_id = page.layout_id
        return instance


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

