from pyramid.events import subscriber
from pyramid.events import BeforeRender

# from altaircms.auth.helpers import user_context
from . import helpers

@subscriber(BeforeRender)
def add_renderer_globals(event):
    event['h'] = helpers
    # event['user'] = user_context(event)
    if event["request"]:
        event['user'] = event["request"].user

from wtforms.form import Form
@subscriber(BeforeRender)
def after_form_initialize(event):
    request = event["request"]
    rendering_val = event.rendering_val
    for k, v in rendering_val.iteritems():
        if isinstance(v, Form):
            request.registry.notify(AfterFormInitialize(v, request, rendering_val))

from altaircms.lib.formevent import AfterFormInitialize
@subscriber(AfterFormInitialize)
def add_choices_query(event):
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

    
