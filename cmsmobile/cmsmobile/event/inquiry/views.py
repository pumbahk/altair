# -*- coding: utf-8 -*-
from pyramid.view import view_config
from cmsmobile.event.inquiry.forms import InquiryForm
from cmsmobile.core.helper import log_info

@view_config(route_name='inquiry', request_method="GET",
             renderer='cmsmobile:templates/inquiry/inquiry.mako')
def move_inquiry(request):
    log_info("move_inquiry", "start")
    form = InquiryForm()
    log_info("move_inquiry", "end")
    return {'form':form}
