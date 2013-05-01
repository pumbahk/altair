from . import SESSION_NAME
from datetime import datetime
import logging
logger = logging.getLogger(__name__)

def set_uploaded_at(after_s3_upload):
    event = after_s3_upload
    session = event.session
    if session.marker != SESSION_NAME:
        return

    layouts = event.extra_args
    logger.warn("*debug set_uploaded_at start. layouts={0}".format(layouts))
    now = datetime.now()
    for layout in layouts:
        layout.uploaded_at = now
