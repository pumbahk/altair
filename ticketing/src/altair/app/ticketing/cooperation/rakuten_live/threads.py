import threading

from altair.app.ticketing.cooperation.rakuten_live.actions import build_r_live_order_data, build_r_live_entry_data, \
    send_r_live_data
from altair.app.ticketing.cooperation.rakuten_live.interfaces import IRakutenLiveApiCommunicator
from altair.app.ticketing.cooperation.rakuten_live.utils import pop_r_live_session


def start_r_live_order_thread(request, order):
    # pop R-Live session to revoke
    r_live_session = pop_r_live_session(request)
    # user bought different performance's ticket from what registered in R-Live CMS
    if not r_live_session or order.performance.id != r_live_session.performance_id:
        return

    data = build_r_live_order_data(order, r_live_session)
    communicator = request.registry.getUtility(IRakutenLiveApiCommunicator)
    t = threading.Thread(target=send_r_live_data, args=(communicator, data, r_live_session, order.order_no))
    t.daemon = True
    t.start()


def start_r_live_entry_thread(request, entry):
    # pop R-Live session to revoke
    r_live_session = pop_r_live_session(request)
    # user applied for different lottery from what registered in R-Live CMS
    if not r_live_session or entry.lot.id != r_live_session.lot_id:
        return

    data = build_r_live_entry_data(entry, r_live_session)
    communicator = request.registry.getUtility(IRakutenLiveApiCommunicator)
    t = threading.Thread(target=send_r_live_data, args=(communicator, data, r_live_session, entry.entry_no))
    t.daemon = True
    t.start()
