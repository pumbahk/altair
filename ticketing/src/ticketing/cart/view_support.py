# -*- coding:utf-8 -*-

""" PC/Mobile のスーパービュークラス
"""
import logging
from pyramid.httpexceptions import HTTPFound
from ticketing.core import models as c_models
from .exceptions import (
    CartException, 
    NoCartError, 
    NoEventError,
    NoPerformanceError,
    NoSalesSegment,
    InvalidCSRFTokenException, 
    OverQuantityLimitError, 
    ZeroQuantityError, 
    CartCreationException,
    OutTermSalesException,
    DeliveryFailedException,
)


logger = logging.getLogger(__name__)

class IndexViewMixin(object):

    def prepare(self):
        if self.context.event is None:
            raise NoEventError(self.context.event_id)

        from .api import get_event_info_from_cms
        self.event_extra_info = get_event_info_from_cms(self.request, self.context.event_id)
        logger.info(self.event_extra_info)

    def check_redirect(self, mobile):
        performance_id = self.request.params.get('pid') or self.request.params.get('performance')

        if performance_id:
            specified = c_models.Performance.query.filter(c_models.Performance.id==performance_id).filter(c_models.Performance.public==True).first()
            if mobile:
                if specified is not None and specified.redirect_url_mobile:
                    raise HTTPFound(specified.redirect_url_mobile)
            else:
                if specified is not None and specified.redirect_url_pc:
                    raise HTTPFound(specified.redirect_url_pc)

def get_amount_without_pdmp(cart):
    return sum([cp.product.price * cp.quantity for cp in cart.products])

