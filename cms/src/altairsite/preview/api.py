from altair.preview.api import set_rendered_target
from altair.preview.api import get_rendered_target

def set_rendered_event(request, event):
    set_rendered_target(request, "event", event)

def set_rendered_page(request, page):
    set_rendered_target(request, "page", page)
    
