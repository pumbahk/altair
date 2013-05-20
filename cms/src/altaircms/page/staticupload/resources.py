from datetime import datetime
from altaircms.models import DBSession
import altaircms.security as security
from .. import models
from altaircms.subscribers import notify_model_create
from .api import get_static_page_utility
from altaircms.viewlib import get_endpoint

class StaticPageResource(security.RootFactory):
    def form(self, formclass, *args, **kwargs):
        form = formclass(*args, **kwargs)
        form.configure(self.request)
        return form

    def creation(self, creation, *args, **kwargs):
        static_directory = get_static_page_utility(self.request)
        return creation(self.request, static_directory, 
                        *args, **kwargs)

    def touch(self, obj, _now=datetime.now):
        obj.updated_at = _now()
        DBSession.add(obj)
        return obj

    def endpoint(self, static_page):
        return get_endpoint(self.request) or self.request.route_url("static_pageset", action="detail", static_page_id=static_page.pageset.id)
