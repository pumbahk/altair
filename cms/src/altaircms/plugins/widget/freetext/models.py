from altaircms.interfaces import IWidget
from zope.interface import implements
from altaircms.plugins.base import Base
from altaircms.plugins.base import DBSession
from altaircms.plugins.base import HandleSessionMixin
from altaircms.plugins.base import UpdateDataMixin

import sqlalchemy as sa

class FreetextWidget(Base):
    implements(IWidget)
    type = "freetext"
    template_name = "altaircms.plugins.widget:freetext/render.mako"    

    query = DBSession.query_property()
    __tablename__ = "widget_text"
    id = sa.Column(sa.Integer, primary_key=True)
    text = sa.Column(sa.Unicode)

    def __init__(self, id=None, text=None):
        self.id = id
        self.text = text

class FreetextWidgetResource(HandleSessionMixin, UpdateDataMixin):
    def __init__(self, request):
        self.request = request

    def _get_or_create(self, model, widget_id):
        if widget_id is None:
            return model()
        else:
            return DBSession.query(model).filter(model.id == widget_id).one()
        
    def get_freetext_widget(self, widget_id):
        return self._get_or_create(FreetextWidget, widget_id)

