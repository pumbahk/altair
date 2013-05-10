from . import SESSION_NAME
from datetime import datetime
import logging
from functools import wraps
from altairsite.front.api import get_frontpage_discriptor_resolver
from altaircms.filelib.core import SignaturedFile
logger = logging.getLogger(__name__)

def only_layout(fn):
    @wraps(fn)
    def wrapped(event):
        session = event.session
        if session.marker != SESSION_NAME:
            return
        return fn(event)
    return wrapped

@only_layout
def set_uploaded_at(after_s3_upload):
    event = after_s3_upload
    layouts = event.extra_args
    logger.warn("*debug set_uploaded_at start. layouts={0}".format(layouts))
    now = datetime.now()
    for layout in layouts:
        layout.uploaded_at = now

@only_layout
def rename_for_s3_upload(before_s3_upload):
    event = before_s3_upload
    request = event.request
    layouts = event.extra_args
    layout_dict = {l.prefixed_template_filename:l for l in layouts}

    resolver = get_frontpage_discriptor_resolver(request)
    updated = []
    for f, realpath in event.files:
        name = f.name
        if not name in layout_dict:
            updated.append((f, realpath))
        else:
            layout = layout_dict[name]
            descriptor = resolver.resolve(request, layout)
            updated_name = descriptor.absspec()
            updated.append((SignaturedFile(name=updated_name, handler=f.handler, signature=f.signature), realpath))
            logger.warn("*debug rename_for_s3_upload: change name {0} -> {1}".format(name, updated_name))
    event.files = updated
