from . import SESSION_NAME
from datetime import datetime
import logging
from functools import wraps
from altaircms.filelib.s3 import Renamer
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
    logger.info("*debug set_uploaded_at start. layouts={0}".format(layouts))
    now = datetime.now()
    for layout in layouts:
        layout.uploaded_at = now

def make_s3_upload_filename(request, name):
    return  u"{}/{}".format(SESSION_NAME, name.lstrip("/"))

@only_layout
def rename_for_s3_upload(before_s3_upload):
    event = before_s3_upload
    # RT/test.html -> cms-layout-templates/RT/test.html
    renamer = Renamer(event.request, event)
    renamer.rename(make_s3_upload_filename)
