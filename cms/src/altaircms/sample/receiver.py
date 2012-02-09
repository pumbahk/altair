from pyramid.events import subscriber
from pyramid.events import BeforeRender
from . import helpers

@subscriber(BeforeRender)
def add_renderer_globals(event):
    event['h'] = helpers
