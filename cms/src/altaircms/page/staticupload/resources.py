from datetime import datetime
from altaircms.models import DBSession
import altaircms.security as security
from .. import models
from altaircms.subscribers import notify_model_create

class StaticPageResource(security.RootFactory):
    def create_static_page(self, data):
        static_page = models.StaticPage(name=data["name"],
                                        layout=data["layout"],
                                        label=data["label"],
                                        publish_begin=data["publish_begin"],
                                        publish_end=data["publish_end"],
                                        interceptive=data["interceptive"]
                                        )
        DBSession.add(static_page)
        notify_model_create(self.request, static_page, data)
        DBSession.flush()
        return static_page

    def touch_static_page(self, static_page, _now=datetime.now):
        static_page.updated_at = _now()
        DBSession.add(static_page)
        return static_page

    def delete_static_page(self, static_page):
        DBSession.delete(static_page)
