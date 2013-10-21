# -*- coding:utf-8 -*-
from zope.interface import implementer
from collections import namedtuple
from altair.app.ticketing.helpers import label_text_for 
from .interfaces import (
    IDescriptionItem, 
)

DescriptionItem = implementer(IDescriptionItem)(namedtuple("DescriptionItem", "name display_name value"))

def columns_of(model):
    return model.__class__.__table__.columns


def organization_description(organization):
    fields = ["name"]
    columns = columns_of(organization)
    return [DescriptionItem(name=name, value=getattr(organization, name), display_name=u"Organization:{}".format(label_text_for(columns[name])))
            for name in fields]
    

def event_description(event):
    fields = ["title"]
    columns = columns_of(event)
    return [DescriptionItem(name=name, value=getattr(event, name), display_name=u"イベント:{}".format(label_text_for(columns[name])))
            for name in fields]

def performance_description(performance):
    columns = columns_of(performance)
    venue_columns = columns_of(performance.venue)
    r = []
    name = "name"
    r.append(DescriptionItem(name=name, value=getattr(performance, name), display_name=u"公演:{}".format(label_text_for(columns[name]))))
    name = "start_on"
    r.append(DescriptionItem(name=name, value=getattr(performance, name), display_name=u"公演:{}".format(label_text_for(columns[name]))))
    ## venue
    name = "name"
    r.append(DescriptionItem(name=name, value=getattr(getattr(performance, "venue"), name), display_name=u"公演:{}".format(label_text_for(venue_columns[name]))))
    return r
