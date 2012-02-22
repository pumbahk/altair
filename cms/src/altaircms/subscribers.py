from pyramid.events import subscriber
from pyramid.events import BeforeRender

from altaircms.auth.helpers import user_context
from . import helpers

@subscriber(BeforeRender)
def add_renderer_globals(event):
    event['h'] = helpers
    event['user'] = user_context(event)

