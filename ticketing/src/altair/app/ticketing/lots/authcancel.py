import logging
from zope.interface import implementer
from altair.multicheckout.interfaces import ICancelFilter
from .models import LotEntry

logger = logging.getLogger(__name__)

def includeme(config):
    config.registry.registerUtility(CancelFilter(), name="lots")

@implementer(ICancelFilter)
class CancelFilter(object):
    def is_cancelable(self, order_no):
        logger.debug('check lot authority order no = {0}'.format(order_no))

        return not LotEntry.query.filter(
            LotEntry.entry_no.startswith(order_no),
        ).filter(
            LotEntry.closed_at==None
        ).count()
