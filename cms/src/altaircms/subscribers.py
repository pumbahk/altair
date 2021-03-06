from altaircms.formhelpers import Form
# from altaircms.auth.helpers import user_context
from . import helpers
from interfaces import IAfterFormInitialize
from zope.interface import implementer 

@implementer(IAfterFormInitialize)
class AfterFormInitialize(object):
    def __init__(self, form, request, rendering_val):
        self.form = form
        self.request = request
        self.rendering_val = rendering_val

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

    for k, v in form._fields.iteritems():
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

from altaircms.auth.helpers import get_authenticated_organization

def add_request_organization_id(self):
    if hasattr(self.obj, "organization_id"):
        organization = get_authenticated_organization(self.request)
        if organization is not None:
            self.obj.organization_id = organization.id
