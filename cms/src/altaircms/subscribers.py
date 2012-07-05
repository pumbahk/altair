from altaircms.lib.formevent import AfterFormInitialize
from wtforms.form import Form
# from altaircms.auth.helpers import user_context
from . import helpers

def add_renderer_globals(event):
    event['h'] = helpers
    # event['user'] = user_context(event)
    # if event["request"]:
    #     event['user'] = event["request"].user


def after_form_initialize(event):
    request = event["request"]
    rendering_val = event.rendering_val
    if hasattr(rendering_val, "iteritems"):
        for k, v in rendering_val.iteritems():
            if isinstance(v, Form):
                request.registry.notify(AfterFormInitialize(v, request, rendering_val))


def add_choices_query_refinement(event): #todo:refactoring
    form = event.form
    form_class = form.__class__

    request = event.request
    rendering_val = event.rendering_val
    for k, v in form.__dict__.iteritems():
        if k.startswith("_"):
            continue
        if hasattr(form_class, k):
            dynamic_query = getattr(getattr(form_class, k), "_dynamic_query", None)
            if dynamic_query:
                dynamic_query(v, form=form, rendering_val=rendering_val, request=request)

from altaircms.interfaces import IModelEvent
from zope.interface import implementer

@implementer(IModelEvent)
class ModelCreate(object):
    def __init__(self, request, obj, params=None):
        self.request = request
        self.obj = obj
        self.params = params

def notify_model_create(request, obj, params=None):
    registry = request.registry
    return registry.notify(ModelCreate(request, obj, params))

def add_request_organization_id(self):
    if hasattr(self.obj, "organization_id"):
        self.obj.organization_id = self.request.organization.id
