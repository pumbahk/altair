# coding: utf-8
from sqlalchemy.sql.expression import desc

from altaircms.models import DBSession
from altaircms.widget.models import Widget
from altaircms.widget.mappers import *

def get_mapper_cls(widget):
    try:
        return globals()[widget.type.capitalize() + 'WidgetMapper']
    except KeyError:
        return None


def get_widget_list(site_id=None):
    objects = DBSession.query(Widget).order_by(desc(Widget.id)).all()
    return objects
