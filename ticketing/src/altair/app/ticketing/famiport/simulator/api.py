from sqlalchemy.orm.exc import NoResultFound
from altair.sqlahelper import get_db_session
from lxml import etree, builder
from urllib2 import urlopen, Request
from base64 import b64decode
from ..communication.utils import FamiPortCrypt
from .interfaces import IFamiPortCommunicator, IFamiPortClientConfigurationRegistry, IMmkSequence
from .models import FDCSideOrder, FDCSideTicket
from .exceptions import FDCAPIError

def get_communicator(request):
    return request.registry.queryUtility(IFamiPortCommunicator)

def get_client_configuration_registry(request):
    return request.registry.queryUtility(IFamiPortClientConfigurationRegistry)

def get_mmk_sequence(request):
    return request.registry.queryUtility(IMmkSequence)

def store_payment_result(request, store_code, mmk_no, type, client_code, total_amount, ticket_payment, system_fee, ticketing_fee, order_id, barcode_no, exchange_no, ticketing_start_at, ticketing_end_at, kogyo_name, koen_date, tickets):
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
            ]
        )
    session.add(fdc_side_order)
    session.commit()

def get_payment_result(request, store_code, barcode_no):
    session = get_db_session(request, 'famiport_mmk')

    q = session.query(FDCSideOrder) \
        .filter(FDCSideOrder.store_code == store_code)

    q = q.filter((FDCSideOrder.barcode_no == barcode_no) | (FDCSideOrder.exchange_no == barcode_no))
    for fdc_side_order in q:
        if fdc_side_order.valid_barcode_no == barcode_no:
            return fdc_side_order
    return None

def save_payment_result(request, payment_result):
    session = get_db_session(request, 'famiport_mmk')
    session.add(payment_result)
    session.commit()

def get_ticket_preview_picture(request, url, discrimination_code, client_code, order_id, name, member_id, address_1, address_2, identify_no, tickets, response_image_type):
    c = FamiPortCrypt(order_id)
    E = builder.E
    request_body = '<?xml version="1.0" encoding="Shift_JIS" ?>' + \
        etree.tostring(
            E.FMIF(
                E.playGuideCode(discrimination_code.zfill(2)),
                E.clientId(client_code.zfill(24)),
                E.barCodeNo(barcode_no),
                E.name(c.encrypt(name)),
                E.memberId(c.encrypt(member_id)),
                E.address1(c.encrypt(address_1)),
                E.address2(c.encrypt(address_2)),
                E.identifyNo(identify_no),
                E.responseImageType(response_image_type),
                *(
                    E.ticket(
                        E.barCodeNo(ticket['barcode_no']),
                        E.templateCode(ticket['template_code']),
                        E.ticketData(ticket['data'])
                        )
                    for ticket in tickets
                    )
                ),
            encoding='unicode'
            ).encode('CP932')
    request = Request(url, request_body, headers={'Content-Type': 'text/xml; charset=Shift_JIS'})
    response = urlopen(request)
    xml = lxml.parse(response)
    result_code_node = xml.find('resultCode')
    if result_code_node is None:
        raise FDCAPIError('invalid response')
    if result_code_node.text != u'00':
        raise FDCAPIError('server returned error status (%s)' % result_code_node.text)
    return [
        b64decode(encoded_ticket_preview_pictures)
        for encoded_ticket_preview_pictures in xml.findall('kenmenData')
        ]

