# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)

def dict_from_event(event):
    return {"id": event.id, "name": event.title}
