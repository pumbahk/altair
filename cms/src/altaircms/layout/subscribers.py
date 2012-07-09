
from altaircms.subscribers import notify_model_create
from zope.interface import implementer
from altaircms.interfaces import IModelEvent
from .interfaces import ILayoutCreator
from . import api
from ..models import DBSession
from altaircms.lib.viewhelpers import FlashMessage

@implementer(IModelEvent)
class LayoutCreate(object):
    def __init__(self, request, obj, params=None):
        self.request = request
        self.obj = obj
        self.params = params

def notify_layout_create(request, params=None):
    registry = request.registry
    return registry.notify(LayoutCreate(request, None, params))

def create_template_layout(self):
    layout_creator = api.get_layout_creator(self.request)
    layout_creator = self.request.registry.getUtility(ILayoutCreator)
    layout_creator.create_file(self.params) ##
    layout = layout_creator.create_model(self.params)
    DBSession.add(layout)
    FlashMessage.success("create layout %s" % layout.title, request=self.request)
    notify_model_create(self.request, layout, self.params)

