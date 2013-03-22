# -*- coding:utf-8 -*-

from altaircms.interfaces import IWidget
import logging
logger = logging.getLogger(__file__)
from zope.interface import implements
import sqlalchemy as sa
import sqlalchemy.orm as orm
from altaircms.widget.models import Widget
from altaircms.plugins.base import DBSession
from altaircms.plugins.base.mixins import HandleSessionMixin
from altaircms.plugins.base.mixins import HandleWidgetMixin
from altaircms.plugins.base.mixins import UpdateDataMixin
from altaircms.security import RootFactory

from altaircms.tag.api import get_tagmanager
from altaircms.plugins.widget.api import get_rendering_function_via_page
        
class TopcontentWidget(Widget):
    implements(IWidget)
    type = "topcontent"

    __tablename__ = "widget_topcontent"
    __mapper_args__ = {"polymorphic_identity": type}
    query = DBSession.query_property()

    def __init__(self, *args, **kwargs):
        super(TopcontentWidget, self).__init__(*args, **kwargs)
        if not "rendering_image_attribute":
            self.rendering_image_attribute = "thumbnail_path" #xxx:
        if not "display_count":
            self.display_count = 6 

    id = sa.Column(sa.Integer, sa.ForeignKey("widget.id"), primary_key=True)
    display_type = sa.Column(sa.Unicode(length=255))
    display_count = sa.Column(sa.Integer)
    tag_id = sa.Column(sa.Integer, sa.ForeignKey("topiccoretag.id"))
    tag = orm.relationship("TopcontentTag", uselist=False, primaryjoin="TopcontentWidget.tag_id==TopcontentTag.id")
    system_tag_id = sa.Column(sa.Integer, sa.ForeignKey("topiccoretag.id"))
    rendering_image_attribute = sa.Column(sa.String(length=16), nullable=False, default="thumbnail_path")
    system_tag = orm.relationship("TopcontentTag", uselist=False, primaryjoin="TopcontentWidget.system_tag_id==TopcontentTag.id")

    def merge_settings(self, bname, bsettings):
        ## lookup utilities.py
        closure = get_rendering_function_via_page(self, bname, bsettings, self.type)
        bsettings.add(bname, closure)

        
class TopcontentWidgetResource(HandleSessionMixin,
                          UpdateDataMixin,
                          HandleWidgetMixin,
                          RootFactory
                          ):
    WidgetClass = TopcontentWidget
    @property
    def Tag(self):
        return get_tagmanager(self.WidgetClass.type, request=self.request).Tag
    def get_widget(self, widget_id):
        return self._get_or_create(TopcontentWidget, widget_id)
