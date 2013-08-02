from pyramid import testing
def _dummy_request():
    from altair.app.ticketing.core.models import Organization, Event

    organization = Organization(short_name="testing")
    event = Event(organization=organization)
    user = testing.DummyModel(organization=organization)

    request = testing.DummyRequest()
    context = testing.DummyResource(event=event,
                                    user=user)
    request.context = context
    return request

def _entry(email=None, lot=None, entry_no=None,
           elected_at=None, canceled_at=None, rejected_at=None):
    from altair.app.ticketing.core.models import ShippingAddress
    from altair.app.ticketing.lots.models import LotEntry
    return LotEntry(lot=lot,
                    entry_no=entry_no,
                    elected_at=elected_at,
                    canceled_at=canceled_at,
                    rejected_at=rejected_at,
                    shipping_address=ShippingAddress(email_1=email))

def _wish(email=None, lot=None, entry_no=None, wish_order=0,
           elected_at=None, canceled_at=None, rejected_at=None):
    from altair.app.ticketing.lots.models import LotEntryWish
    entry = _entry(email, lot=lot, entry_no=entry_no,
                   elected_at=elected_at,
                   rejected_at=rejected_at,
                   canceled_at=canceled_at)
    wish = LotEntryWish(lot_entry=entry,
                        elected_at=elected_at,
                        rejected_at=rejected_at,
                        canceled_at=canceled_at,
                        wish_order=wish_order)
    return wish
