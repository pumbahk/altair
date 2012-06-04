# from altaircms.auth.helpers import user_context
from altaircms import helpers

def add_renderer_globals(event):
    event['h'] = helpers
