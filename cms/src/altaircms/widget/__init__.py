# coding: utf-8
from sqlalchemy.sql.expression import desc

from altaircms.models import DBSession
from altaircms.widget.models import Widget
from altaircms.widget.mappers import *
from altaircms.asset.models import *

def widget_convert_to_dict(widget):
    cls = globals()[widget.type.capitalize() + 'WidgetMapper'](widget)
    return {widget.type: cls.as_dict()}

def get_widget_list(site_id=None):
    objects = DBSession.query(Widget).order_by(desc(Widget.id)).all()
    return objects
