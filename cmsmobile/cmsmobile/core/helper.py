# -*- coding: utf-8 -*-
import webhelpers.paginate as paginate

def exist_value(value):

    if value is None:
        return False

    if value == "":
        return False

    if value == "0":
        return False

    if value == 0:
        return False

    return True

def get_week_map():
    return {0:u'月',1:u'火',2:u'水',3:u'木',4:u'金',5:u'土',6:u'日'}

def get_event_paging(request, form, qs):
    events = None
    form.num.data = 0
    if qs:
        events = qs.all()

        if events:
            form.num.data = len(events)
            items_per_page = 10
            form.events.data = paginate.Page(
                events,
                form.page.data,
                items_per_page,
                url=paginate.PageURL_WebOb(request)
            )
            if form.num.data % items_per_page == 0:
                form.page_num.data = form.num.data / items_per_page
            else:
                form.page_num.data = form.num.data / items_per_page + 1

    return form
