from altaircms.models import DBSession
from altaircms.interfaces import IHandleSession
from altaircms.interfaces import IHandleWidget
from altaircms.interfaces import IUpdateData
from zope.interface import implements

class HandleSessionMixin(object):
    implements(IHandleSession)
    session = DBSession
    def add(self, data, flush=False):
        self.session.add(data)
        if flush:
            self.session.flush()
        
    def delete(self, data, flush=False):
        self.session.delete(data)
        if flush:
            self.session.flush()

class HandleWidgetMixin(object):
    implements(IHandleWidget)
    WidgetClass = None
    def _get_or_create(self, model, widget_id):
        if widget_id is None:
            return model()
        else:
            return DBSession.query(model).filter(model.id == widget_id).one()
        
    def get_widget(self, widget_id):
        return self._get_or_create(self.WidgetClass, widget_id)


class UpdateDataMixin(object):
    implements(IUpdateData)
    def update_data(self, data, **kwargs):
        for k, v in kwargs.items():
            setattr(data, k, v)
        return data
    update = update_data # deperecated
