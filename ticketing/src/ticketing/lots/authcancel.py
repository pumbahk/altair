from ticketing.multicheckout.interfaces import ICancelFilter
from zope.interface import implementer
from .models import LotEntry

def include(config):
    config.registry.registerUtility(CancelFilter)

@implementer(ICancelFilter)
class CancelFilter(object):
    def is_cancelable(self, order_no):
        return not LotEntry.query.filter(LotEntry.order_no==order_no).count()
