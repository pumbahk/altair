from zope.interface import implementer
from ticketing.multicheckout.interfaces import ICancelFilter
from .models import LotEntry

def includeme(config):
    config.registry.registerUtility(CancelFilter())

@implementer(ICancelFilter)
class CancelFilter(object):
    def is_cancelable(self, order_no):
        return not LotEntry.query.filter(
            LotEntry.entry_no==order_no,
        ).filter(
            LotEntry.closed_at==None
        ).count()
