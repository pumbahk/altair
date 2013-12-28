# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)

def dict_from_performance(performance):
    return {"id": performance.id, 
            "name": performance.name, 
            "event_id": performance.event_id, 
            "start_on": performance.start_on, 
            "end_on": performance.end_on
        }


