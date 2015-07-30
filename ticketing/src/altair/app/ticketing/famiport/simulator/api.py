from sqlalchemy.orm.exc import NoResultFound
from altair.sqlahelper import get_db_session
from .interfaces import IFamiPortCommunicator, IFamiPortClientConfigurationRegistry, IMmkSequence
from .models import FDCSideOrder, FDCSideTicket

def get_communicator(request):
    return request.registry.queryUtility(IFamiPortCommunicator)

def get_client_configuration_registry(request):
    return request.registry.queryUtility(IFamiPortClientConfigurationRegistry)

def get_mmk_sequence(request):
    return request.registry.queryUtility(IMmkSequence)

def store_payment_result(request, store_code, mmk_no, type, client_code, total_amount, ticket_payment, system_fee, ticketing_fee, order_id, barcode_no, exchange_no, ticketing_start_at, ticketing_end_at, kogyo_name, koen_date, tickets, payment_sheet_text):
    session = get_db_session(request, 'famiport_mmk')
    if session.query(FDCSideOrder) \
       .filter(FDCSideOrder.store_code == store_code) \
       .filter(FDCSideOrder.barcode_no == barcode_no) \
       .filter(FDCSideOrder.exchange_no == exchange_no) \
       .first() is not None:
        return 

    fdc_side_order = FDCSideOrder(
        store_code=store_code,
        mmk_no=mmk_no,
        client_code=client_code,
        total_amount=total_amount,
        ticket_payment=ticket_payment,
        system_fee=system_fee,
        ticketing_fee=ticketing_fee,
        type=type,
        order_id=order_id,
        barcode_no=barcode_no,
        exchange_no=exchange_no,
        kogyo_name=kogyo_name,
        koen_date=koen_date,
        ticketing_start_at=ticketing_start_at,
        ticketing_end_at=ticketing_end_at,
        paid_at=None,
        issued_at=None,
        fdc_side_tickets=[
            FDCSideTicket(
                type=ticket['ticketClass'],
                barcode_no=ticket['barCodeNo'],
                template_code=ticket['templateCode'],
                data=ticket['ticketData']
                )
            for ticket in tickets
            ] if tickets else [],
        payment_sheet_text=payment_sheet_text
        )
    session.add(fdc_side_order)
    session.commit()

def get_payment_result_by_id(request, order_id):
    session = get_db_session(request, 'famiport_mmk')
    q = session.query(FDCSideOrder).filter(FDCSideOrder.id == order_id)
    try:
        return q.one()
    except NoResultFound:
        return None

def get_payment_result(request, store_code, barcode_no):
    session = get_db_session(request, 'famiport_mmk')

    q = session.query(FDCSideOrder) \
        .filter(FDCSideOrder.store_code == store_code)

    q = q.filter((FDCSideOrder.barcode_no == barcode_no) | (FDCSideOrder.exchange_no == barcode_no))
    for fdc_side_order in q:
        if fdc_side_order.valid_barcode_no == barcode_no:
            return fdc_side_order
    return None

def get_payment_results(request):
    session = get_db_session(request, 'famiport_mmk')

    q = session.query(FDCSideOrder)
    return q

def save_payment_result(request, payment_result):
    session = get_db_session(request, 'famiport_mmk')
    session.add(payment_result)
    session.commit()

def gen_serial_for_store(request, now, store_code):
    mmk_seq = get_mmk_sequence(request) 
    serial = mmk_seq.next_serial(now, store_code)
    return u'%02d%02d%02d%05d' % (
        now.year % 100,
        now.month,
        now.day,
        serial
        )

