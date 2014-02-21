import transaction
import logging
logger = logging.getLogger(__name__)

class DeliveryErrorEvent(object):
    def __init__(self, exception, request, order):
        self.exception = exception
        self.request = request
        self.order = order


def cancel_on_delivery_error(event):
    import sqlahelper

    e = event.exception
    request = event.request
    order = event.order

    logger.exception('order canceled because of fatal error (%r)' % e)

    order.cancel(request)
    order.note = str(e)
    
    DBSession = sqlahelper.get_session()
    DBSession.expunge_all()
    transaction.commit()
